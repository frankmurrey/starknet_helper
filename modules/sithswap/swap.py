import time
from typing import Union
from typing import TYPE_CHECKING

from starknet_py.net.account.account import Account
from loguru import logger

from contracts.sithswap.main import SithSwapContracts
from modules.base import SwapModuleBase
from modules.sithswap.base import SithBase
from utils.get_delay import get_delay
from src.schemas.action_models import ModuleExecutionResult, TransactionPayloadData

if TYPE_CHECKING:
    from src.schemas.tasks.sithswap import SithSwapTask
    from src.schemas.wallet_data import WalletData


class SithSwap(SithBase, SwapModuleBase):
    task: 'SithSwapTask'
    account: Account

    def __init__(
            self,
            account,
            task: 'SithSwapTask',
            wallet_data: 'WalletData',
    ):

        super().__init__(
            account=account,
            task=task,
            wallet_data=wallet_data,
        )

        self.task = task
        self.account = account

        self.sith_swap_contracts = SithSwapContracts()
        self.router_contract = self.get_contract(
            address=self.sith_swap_contracts.router_address,
            abi=self.sith_swap_contracts.router_abi,
            provider=account
        )

    async def build_txn_payload_data(self) -> Union[TransactionPayloadData, None]:
        """
        Build the transaction payload data for the swap type transaction.
        :return:
        """
        amount_x_wei = await self.calculate_amount_out_from_balance(coin_x=self.coin_x)
        if amount_x_wei is None:
            self.log_error(f"Error while calculating amount out from balance of {self.coin_x.symbol.upper()}")
            return None

        amounts_in_data: dict = await self.get_direct_amount_in_and_pool_type(
            amount_in_wei=amount_x_wei,
            coin_x=self.coin_x,
            coin_y=self.coin_y,
            router_contract=self.router_contract
        )
        if amounts_in_data is None:
            self.log_error(f"Error while getting direct amount in and pool type of {self.coin_x.symbol.upper()}")
            return None

        amount_in = amounts_in_data['amount_in_wei']
        amount_in_wei_with_slippage = int(amount_in * (1 - (self.task.slippage / 100)))
        is_stable = amounts_in_data["stable"]

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
                       1,
                       self.i16(self.coin_x.contract_address),
                       self.i16(self.coin_y.contract_address),
                       is_stable,
                       self.account.address,
                       swap_deadline]
        )
        calls = [approve_call, swap_call]

        return TransactionPayloadData(
            calls=calls,
            amount_x_decimals=amount_x_wei / 10 ** self.token_x_decimals,
            amount_y_decimals=amount_in / 10 ** self.token_y_decimals,
        )

    async def build_reverse_txn_payload_data(self) -> Union[TransactionPayloadData, None]:
        """
        Build the transaction payload data for the reverse swap type transaction, if reverse action is enabled in task.
        :return:
        """
        wallet_y_balance_wei = await self.get_token_balance(token_address=self.coin_y.contract_address,
                                                            account=self.account)
        if wallet_y_balance_wei == 0:
            self.log_error(f"Wallet {self.coin_y.symbol.upper()} balance = 0")
            return None

        if self.initial_balance_y_wei is None:
            self.log_error(f"Error while getting initial balance of {self.coin_y.symbol.upper()}")
            return None

        amount_out_y_wei = wallet_y_balance_wei - self.initial_balance_y_wei
        if amount_out_y_wei <= 0:
            self.log_error(f"Wallet {self.coin_y.symbol.upper()} balance less than initial balance")
            return None

        amounts_y_data = await self.get_direct_amount_in_and_pool_type(
            amount_in_wei=amount_out_y_wei,
            coin_x=self.coin_y,
            coin_y=self.coin_x,
            router_contract=self.router_contract
        )
        if amounts_y_data is None:
            self.log_error(f"Error while getting direct amount in and pool type of {self.coin_y.symbol.upper()}")
            return None

        amount_in = amounts_y_data['amount_in_wei']
        amount_in_wei_with_slippage = int(amount_in * (1 - (self.task.slippage / 100)))
        is_stable = amounts_y_data["stable"]

        approve_call = self.build_token_approve_call(
            token_addr=self.coin_x.contract_address,
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
                       1,
                       self.i16(self.coin_y.contract_address),
                       self.i16(self.coin_x.contract_address),
                       is_stable,
                       self.account.address,
                       swap_deadline]
        )

        calls = [approve_call, swap_call]

        return TransactionPayloadData(
            calls=calls,
            amount_x_decimals=amount_out_y_wei / 10 ** self.token_x_decimals,
            amount_y_decimals=amount_in / 10 ** self.token_y_decimals,
        )
