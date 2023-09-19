import time
from typing import Union
from typing import TYPE_CHECKING

from starknet_py.net.account.account import Account
from loguru import logger

from modules.jediswap.base import JediSwapBase
from utlis.get_delay import get_delay


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

    async def build_txn_payload_data(self) -> Union[dict, None]:
        """
        Build the transaction payload data for the swap type transaction.
        :return:
        """
        amount_out_wei = await self.calculate_amount_out_from_balance(coin_x=self.coin_x)

        amount_in_wei = await self.get_amount_in(
            amount_out_wei=amount_out_wei,
            coin_x_obj=self.coin_x,
            coin_y_obj=self.coin_y,
            router_contract=self.router_contract
        )
        if amount_in_wei is None:
            return None

        amount_in_wei_with_slippage = int(amount_in_wei * (1 - (self.task.slippage / 100)))

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
            'amount_x_decimals': amount_out_wei / 10 ** self.token_x_decimals,
            'amount_y_decimals': amount_in_wei / 10 ** self.token_y_decimals,
        }

    async def build_reverse_txn_payload_data(self) -> Union[dict, None]:
        """
        Build the transaction payload data for the reverse swap type transaction, if reverse action is enabled in task.
        :return:
        """
        wallet_y_balance_wei = await self.get_token_balance(token_address=self.coin_y.contract_address,
                                                            account=self.account)

        if wallet_y_balance_wei == 0:
            logger.error(f"Wallet {self.coin_y.symbol.upper()} balance = 0")
            return None

        amount_out_y_wei = wallet_y_balance_wei - self.initial_balance_y_wei
        if amount_out_y_wei <= 0:
            logger.error(f"Wallet {self.coin_y.symbol.upper()} balance less than initial balance")
            return None

        amount_in_wei = await self.get_amount_in(
            amount_out_wei=amount_out_y_wei,
            coin_x_obj=self.coin_y,
            coin_y_obj=self.coin_x,
            router_contract=self.router_contract
        )
        if amount_in_wei is None:
            return None

        amount_in_wei_with_slippage = int(amount_in_wei * (1 - (self.task.slippage / 100)))

        approve_call = self.build_token_approve_call(token_addr=self.coin_y.contract_address,
                                                     spender=hex(self.router_contract.address),
                                                     amount_wei=int(amount_out_y_wei))

        swap_deadline = int(time.time() + 1000)

        swap_call = self.build_call(to_addr=self.router_contract.address,
                                    func_name='swap_exact_tokens_for_tokens',
                                    call_data=[amount_out_y_wei,
                                               0,
                                               amount_in_wei_with_slippage,
                                               0,
                                               2,
                                               self.i16(self.coin_y.contract_address),
                                               self.i16(self.coin_x.contract_address),
                                               self.account.address,
                                               swap_deadline])
        calls = [approve_call, swap_call]

        return {
            'calls': calls,
            'amount_x_decimals': amount_out_y_wei / 10 ** self.token_y_decimals,
            'amount_y_decimals': amount_in_wei / 10 ** self.token_x_decimals,
        }

    async def send_txn(self):
        """
        Sends swap type transaction, if reverse action is enabled in task, sends reverse swap type transaction
        :return:
        """
        await self.set_fetched_tokens_data()

        if self.check_local_tokens_data() is False:
            return False

        txn_payload_data = await self.build_txn_payload_data()
        if txn_payload_data is None:
            return False

        txn_status = await self.send_swap_type_txn(
            account=self.account,
            txn_payload_data=txn_payload_data
        )

        if txn_status is False:
            return False

        if self.task.reverse_action is True:
            delay = get_delay(self.task.min_delay_sec, self.task.max_delay_sec)
            logger.info(f"Waiting {delay} seconds before reverse action")
            time.sleep(delay)

            reverse_txn_payload_data = await self.build_reverse_txn_payload_data()
            if reverse_txn_payload_data is None:
                return False

            reverse_txn_status = await self.send_swap_type_txn(
                account=self.account,
                txn_payload_data=reverse_txn_payload_data
            )

            return reverse_txn_status
