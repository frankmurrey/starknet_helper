import time
from typing import Union
from typing import TYPE_CHECKING

from contracts.tokens.main import Tokens
from contracts.jediswap.main import JediSwapContracts
from modules.jediswap.base import JediSwapBase
from src.gecko_pricer import GeckoPricer

from starknet_py.net.account.account import Account

if TYPE_CHECKING:
    from src.schemas.tasks.jediswap import JediSwapTask


class JediSwap(JediSwapBase):
    task: 'JediSwapTask'
    account: Account

    def __init__(self,
                 account,
                 task: 'JediSwapTask', ):
        super().__init__(
            account=account,
            task=task,
        )

        self.task = task
        self.account = account

        self.tokens = Tokens()
        self.jedi_contracts = JediSwapContracts()
        self.router_contract = self.get_contract(address=self.jedi_contracts.router_address,
                                                 abi=self.jedi_contracts.router_abi,
                                                 provider=account)

        self.gecko_pricer = GeckoPricer(client=account.client)

        self.coin_x = self.tokens.get_by_name(self.task.coin_to_swap)
        self.coin_y = self.tokens.get_by_name(self.task.coin_to_receive)

    async def build_txn_payload_data(self) -> Union[dict, None]:
        amounts_out: dict = await self.get_amounts_out_from_balance(
            coin_x_obj=self.coin_x,
            use_all_balance=self.task.use_all_balance,
            send_percent_balance=self.task.send_percent_balance,
            min_amount_out=self.task.min_amount_out,
            max_amount_out=self.task.max_amount_out
        )
        if amounts_out is None:
            return None

        amount_out_wei = amounts_out['amount_wei']

        amounts_in = await self.get_amounts_in(
            amount_out_wei=amount_out_wei,
            coin_x_obj=self.coin_x,
            coin_y_obj=self.coin_y,
            router_contract=self.router_contract
        )
        if amounts_in is None:
            return None

        amount_in = amounts_in['amount_wei']
        amount_in_wei_with_slippage = int(amount_in * (1 - (self.task.slippage / 100)))

        approve_call = self.build_token_approve_call(token_addr=self.coin_x.contract_address,
                                                     spender=hex(self.router_contract.address),
                                                     amount_wei=int(amount_out_wei))

        swap_deadline = int(time.time() + 1000)
        swap_call = self.build_call(to_addr=self.router_contract.address,
                                    func_name='swap_exact_tokens_for_tokens',
                                    call_data=[amount_out_wei,
                                               0,
                                               amount_in_wei_with_slippage,
                                               0,
                                               2,
                                               self.i16(self.coin_x.contract_address),
                                               self.i16(self.coin_y.contract_address),
                                               self.account.address,
                                               swap_deadline])
        calls = [approve_call, swap_call]
        return {
            'calls': calls,
            'amount_x_decimals': amounts_out['amount_decimals'],
            'amount_y_decimals': amounts_in['amount_decimals'],
        }

    async def send_txn(self):
        txn_payload_data = await self.build_txn_payload_data()
        if txn_payload_data is None:
            return False

        txn_status = await self.send_swap_type_txn(
            account=self.account,
            txn_payload_data=txn_payload_data
        )

        return txn_status
