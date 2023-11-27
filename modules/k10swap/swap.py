import time
from typing import Union
from typing import TYPE_CHECKING

from loguru import logger
from starknet_py.net.account.account import Account

from utils.get_delay import get_delay
from modules.base import SwapModuleBase
from modules.k10swap.base import K10SwapBase
from src.schemas.action_models import ModuleExecutionResult, TransactionPayloadData


if TYPE_CHECKING:
    from src.schemas.tasks.k10swap import K10SwapTask
    from src.schemas.wallet_data import WalletData


class K10Swap(K10SwapBase, SwapModuleBase):
    task: 'K10SwapTask'
    account: Account

    def __init__(
            self,
            account,
            task: 'K10SwapTask',
            wallet_data: 'WalletData',
    ):

        super().__init__(
            account=account,
            task=task,
            wallet_data=wallet_data
        )

        self.task = task
        self.account = account

    async def build_txn_payload_data(self) -> Union[TransactionPayloadData, None]:
        """
        Build the transaction payload data for the swap type transaction.
        :return:
        """
        amount_x_wei = await self.calculate_amount_out_from_balance(coin_x=self.coin_x)
        if amount_x_wei is None:
            self.log_error(f"Failed to calculate amount out for {self.coin_x.symbol.upper()}")
            return None

        amounts_in_wei = await self.get_amounts_in(
            coin_x=self.coin_x,
            coin_y=self.coin_y,
            amount_in_wei=amount_x_wei
        )
        if amounts_in_wei is None:
            self.log_error(f"Failed to calculate amount in for {self.coin_x.symbol.upper()}")
            return None

        amount_y_wei = amounts_in_wei.amounts[1]
        amount_in_wei_with_slippage = int(amount_y_wei * (1 - (self.task.slippage / 100)))

        approve_call = self.build_token_approve_call(
            token_addr=self.coin_x.contract_address,
            spender=hex(self.router_contract.address),
            amount_wei=int(amount_x_wei)
        )

        swap_deadline = int(time.time() + 1000)
        swap_call = self.build_call(
            to_addr=self.router_contract.address,
            func_name='swapExactTokensForTokens',
            call_data=[amount_x_wei,
                       0,
                       amount_in_wei_with_slippage,
                       0,
                       2,
                       self.i16(self.coin_x.contract_address),
                       self.i16(self.coin_y.contract_address),
                       self.account.address,
                       swap_deadline]
        )
        calls = [approve_call, swap_call]
        return TransactionPayloadData(
            calls=calls,
            amount_x_decimals=amount_x_wei / 10 ** self.token_x_decimals,
            amount_y_decimals=amount_y_wei / 10 ** self.token_y_decimals
        )

    async def build_reverse_txn_payload_data(self) -> Union[TransactionPayloadData, None]:
        """
        Build the transaction payload data for the reverse swap type transaction, if reverse action is enabled in task.
        :return:
        """
        wallet_y_balance_wei = await self.get_token_balance(
            token_address=self.coin_y.contract_address,
            account=self.account
        )
        if wallet_y_balance_wei == 0:
            self.log_error(f"Wallet {self.coin_y.symbol.upper()} balance = 0")

        if self.initial_balance_y_wei is None:
            self.log_error(f"Error while getting initial balance of {self.coin_y.symbol.upper()}")
            return None

        amount_out_y_wei = wallet_y_balance_wei - self.initial_balance_y_wei
        if amount_out_y_wei <= 0:
            self.log_error(f"Wallet {self.coin_y.symbol.upper()} balance less than initial balance")
            return None

        amounts_in_wei = await self.get_amounts_in(
            coin_x=self.coin_y,
            coin_y=self.coin_x,
            amount_in_wei=amount_out_y_wei
        )
        if amounts_in_wei is None:
            self.log_error(f"Failed to calculate amount in for {self.coin_y.symbol.upper()}")
            return None

        amount_in_x_wei = amounts_in_wei.amounts[0]
        amount_in_wei_with_slippage = int(amount_in_x_wei * (1 - (self.task.slippage / 100)))

        approve_call = self.build_token_approve_call(
            token_addr=self.coin_y.contract_address,
            spender=hex(self.router_contract.address),
            amount_wei=int(amount_out_y_wei)
        )

        swap_deadline = int(time.time() + 1000)

        swap_call = self.build_call(
            to_addr=self.router_contract.address,
            func_name='swapExactTokensForTokens',
            call_data=[amount_out_y_wei,
                       0,
                       amount_in_wei_with_slippage,
                       0,
                       2,
                       self.i16(self.coin_y.contract_address),
                       self.i16(self.coin_x.contract_address),
                       self.account.address,
                       swap_deadline]
        )

        calls = [approve_call, swap_call]
        return TransactionPayloadData(
            calls=calls,
            amount_x_decimals=amount_out_y_wei / 10 ** self.token_x_decimals,
            amount_y_decimals=amount_in_x_wei / 10 ** self.token_y_decimals
        )
