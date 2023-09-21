import time
import random
from typing import Union
from typing import TYPE_CHECKING

from starknet_py.net.account.account import Account
from loguru import logger

from contracts.k10swap.main import K10SwapContracts
from modules.base import SwapModuleBase
from utils.get_delay import get_delay


if TYPE_CHECKING:
    from src.schemas.tasks.k10swap import K10SwapTask


class K10Swap(SwapModuleBase):
    task: 'K10SwapTask'
    account: Account

    def __init__(self,
                 account,
                 task: 'K10SwapTask'):

        super().__init__(
            account=account,
            task=task,
        )

        self.task = task
        self.account = account

        self.k10_swap_contracts = K10SwapContracts()
        self.router_contract = self.get_contract(address=self.k10_swap_contracts.router_address,
                                                 abi=self.k10_swap_contracts.router_abi,
                                                 provider=account)

    async def get_amount_in(self,
                            amount_in_wei):
        """
        Get amount in wei from router function
        :param amount_in_wei:
        :return:
        """
        path = [int(self.coin_x.contract_address, 16),
                int(self.coin_y.contract_address, 16)]

        try:
            amounts_out = await self.router_contract.functions["getAmountsOut"].call(
                amount_in_wei,
                path
            )

            return amounts_out

        except Exception as e:
            logger.error(f'Error while getting amount in: {e}')
            return None

    async def build_txn_payload_data(self) -> Union[dict, None]:
        """
        Build the transaction payload data for the swap type transaction.
        :return:
        """
        amount_x_wei = await self.calculate_amount_out_from_balance(coin_x=self.coin_x)

        if amount_x_wei is None:
            return None

        amounts_in_wei = await self.get_amount_in(amount_x_wei)

        if amounts_in_wei is None:
            return None

        amount_y_wei = amounts_in_wei.amounts[1]
        amount_in_wei_with_slippage = int(amount_y_wei * (1 - (self.task.slippage / 100)))

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
                                               2,
                                               self.i16(self.coin_x.contract_address),
                                               self.i16(self.coin_y.contract_address),
                                               self.account.address,
                                               swap_deadline])
        calls = [approve_call, swap_call]

        return {
            'calls': calls,
            'amount_x_decimals': amount_x_wei / 10 ** self.token_x_decimals,
            'amount_y_decimals': amount_y_wei / 10 ** self.token_y_decimals,
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

        if self.initial_balance_y_wei is None:
            logger.error(f"Error while getting initial balance of {self.coin_y.symbol.upper()}")
            return None

        amount_out_y_wei = wallet_y_balance_wei - self.initial_balance_y_wei
        if amount_out_y_wei <= 0:
            logger.error(f"Wallet {self.coin_y.symbol.upper()} balance less than initial balance")
            return None

        amounts_in_wei = await self.get_amount_in(amount_out_y_wei)
        if amounts_in_wei is None:
            return None

        amount_in_x_wei = amounts_in_wei.amounts[0]
        amount_in_wei_with_slippage = int(amount_in_x_wei * (1 - (self.task.slippage / 100)))

        approve_call = self.build_token_approve_call(token_addr=self.coin_y.contract_address,
                                                     spender=hex(self.router_contract.address),
                                                     amount_wei=int(amount_out_y_wei))

        swap_deadline = int(time.time() + 1000)

        swap_call = self.build_call(to_addr=self.router_contract.address,
                                    func_name='swapExactTokensForTokens',
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
            'amount_x_decimals': amount_out_y_wei / 10 ** self.token_x_decimals,
            'amount_y_decimals': amount_in_x_wei / 10 ** self.token_y_decimals,
        }

    async def send_txn(self):
        """
        Send swap type transaction
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
