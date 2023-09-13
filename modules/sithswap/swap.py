import time
from typing import Union
from typing import TYPE_CHECKING

from starknet_py.net.account.account import Account

from contracts.tokens.main import Tokens
from contracts.sithswap.main import SithSwapContracts
from modules.base import SwapModuleBase
from modules.sithswap.base import SithBase

if TYPE_CHECKING:
    from src.schemas.tasks.sithswap import SithSwapTask


class SithSwap(SithBase, SwapModuleBase):
    task: 'SithSwapTask'
    account: Account

    def __init__(self,
                 account,
                 task: 'SithSwapTask'):

        super().__init__(
            account=account,
            task=task,
        )

        self.task = task
        self.account = account

        self.tokens = Tokens()
        self.sith_swap_contracts = SithSwapContracts()
        self.router_contract = self.get_contract(address=self.sith_swap_contracts.router_address,
                                                 abi=self.sith_swap_contracts.router_abi,
                                                 provider=account)

        self.coin_x = self.tokens.get_by_name(self.task.coin_to_swap)
        self.coin_y = self.tokens.get_by_name(self.task.coin_to_receive)

    async def build_txn_payload_data(self) -> Union[dict, None]:
        amount_x_wei = await self.get_amount_out_from_balance(
            coin_x=self.coin_x,
            use_all_balance=self.task.use_all_balance,
            send_percent_balance=self.task.send_percent_balance,
            min_amount_out=self.task.min_amount_out,
            max_amount_out=self.task.max_amount_out
        )
        coin_x_decimals = await self.get_token_decimals(contract_address=self.coin_x.contract_address,
                                                        abi=self.coin_x.abi,
                                                        provider=self.account)
        amount_u_decimals = amount_x_wei / 10 ** coin_x_decimals

        if amount_x_wei is None:
            return None

        amounts_y_data = await self.get_direct_amount_in_and_pool_type(
            amount_in_wei=amount_x_wei,
            coin_x=self.coin_x,
            coin_y=self.coin_y,
            router_contract=self.router_contract
        )
        if amounts_y_data is None:
            return None

        amount_in = amounts_y_data['amount_in_wei']
        amount_in_wei_with_slippage = int(amount_in * (1 - (self.task.slippage / 100)))
        coin_y_decimals = await self.get_token_decimals(contract_address=self.coin_y.contract_address,
                                                        abi=self.coin_y.abi,
                                                        provider=self.account)
        amount_y_decimals = amount_in / 10 ** coin_y_decimals

        is_stable = amounts_y_data["stable"]

        approve_call = self.build_token_approve_call(token_addr=self.coin_x.contract_address,
                                                     spender=hex(self.router_contract.address),
                                                     amount_wei=int(amount_x_wei))

        swap_deadline = int(time.time() + 1000)
        swap_call = self.build_call(to_addr=self.router_contract.address,
                                    func_name='swapExactTokensForTokens',
                                    call_data=[amount_x_wei,
                                               0,
                                               amount_in_wei_with_slippage,
                                               0,
                                               1,
                                               self.i16(self.coin_x.contract_address),
                                               self.i16(self.coin_y.contract_address),
                                               is_stable,
                                               self.account.address,
                                               swap_deadline])
        calls = [approve_call, swap_call]

        return {
            'calls': calls,
            'amount_x_decimals': amount_u_decimals,
            'amount_y_decimals': amount_y_decimals,
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
