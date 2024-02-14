import time
from typing import Union
from typing import TYPE_CHECKING

from starknet_py.net.account.account import Account
from loguru import logger

from src.schemas.action_models import ModuleExecutionResult, TransactionPayloadData
from contracts.myswap.main import MySwapContracts
from modules.myswap.base import MySwapBase
from modules.base import SwapModuleBase
from utils.get_delay import get_delay

if TYPE_CHECKING:
    from src.schemas.tasks.myswap import MySwapTask
    from src.schemas.wallet_data import WalletData


class MySwap(MySwapBase, SwapModuleBase):
    task: 'MySwapTask'
    account: Account

    def __init__(
            self,
            account,
            task: 'MySwapTask',
            wallet_data: 'WalletData',
    ):
        super().__init__(
            account=account,
            task=task,
            wallet_data=wallet_data,
        )

        self.task = task
        self.account = account

        self.my_swap_contracts = MySwapContracts()
        self.router_contract = self.get_contract(
            address=self.my_swap_contracts.router_address,
            abi=self.my_swap_contracts.router_abi,
            provider=account
        )

    async def build_txn_payload_data(self) -> Union[TransactionPayloadData, None]:
        """
        Build the transaction payload data for the swap type transaction.
        :return:
        """
        amount_out_wei = await self.calculate_amount_out_from_balance(coin_x=self.coin_x)
        if amount_out_wei is None:
            self.log_error(f"Failed to calculate amount out for {self.coin_x.symbol.upper()}")
            return None

        reserves_data = await self.get_pool_reserves_data(
            coin_x_symbol=self.coin_x.symbol,
            coin_y_symbol=self.coin_y.symbol,
            router_contract=self.router_contract
        )
        if reserves_data is None:
            self.log_error(f"Failed to get reserves data for {self.coin_x.symbol.upper()}")
            return None

        amount_in_and_fee = await self.get_amount_in_and_dao_fee(
            reserves_data=reserves_data,
            amount_out_wei=amount_out_wei,
            coin_x_obj=self.coin_x,
            coin_y_obj=self.coin_y,
        )
        if amount_in_and_fee is None:
            self.log_error(f"Failed to calculate amount in for {self.coin_x.symbol.upper()}")
            return None

        approve_call = self.build_token_approve_call(
            token_addr=self.coin_x.contract_address,
            spender=hex(self.router_contract.address),
            amount_wei=int(amount_out_wei)
        )

        amount_x_wei, dao_fee = amount_in_and_fee

        amount_x_wei_after_slippage = amount_x_wei - (amount_x_wei * int(self.task.slippage) / 100)
        amount_x_wei_after_slippage *= 1 - (dao_fee / 100000)

        swap_call = self.build_call(
            to_addr=self.router_contract.address,
            func_name='swap',
            call_data=[reserves_data['pool_id'],
                       self.i16(self.coin_x.contract_address),
                       amount_out_wei,
                       0,
                       amount_x_wei_after_slippage,
                       0]
        )
        calls = [approve_call, swap_call]

        return TransactionPayloadData(
            calls=calls,
            amount_x_decimals=amount_out_wei / 10 ** self.token_x_decimals,
            amount_y_decimals=amount_x_wei / 10 ** self.token_y_decimals
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
            return None

        if self.initial_balance_y_wei is None:
            self.log_error(f"Error while getting initial balance of {self.coin_y.symbol.upper()}")
            return None

        amount_out_y_wei = wallet_y_balance_wei - self.initial_balance_y_wei
        if amount_out_y_wei <= 0:
            self.log_error(f"Wallet {self.coin_y.symbol.upper()} balance less than initial balance")
            return None

        reserves_data = await self.get_pool_reserves_data(
            coin_x_symbol=self.coin_y.symbol,
            coin_y_symbol=self.coin_x.symbol,
            router_contract=self.router_contract
        )
        if reserves_data is None:
            self.log_error(f"Failed to get reserves data for {self.coin_y.symbol.upper()}")
            return None

        amount_in_and_fee = await self.get_amount_in_and_dao_fee(
            reserves_data=reserves_data,
            amount_out_wei=amount_out_y_wei,
            coin_x_obj=self.coin_y,
            coin_y_obj=self.coin_x
        )
        if amount_in_and_fee is None:
            self.log_error(f"Failed to calculate amount in for {self.coin_y.symbol.upper()}")
            return None

        approve_call = self.build_token_approve_call(
            token_addr=self.coin_y.contract_address,
            spender=hex(self.router_contract.address),
            amount_wei=int(amount_out_y_wei)
        )

        amount_x_wei, dao_fee = amount_in_and_fee

        amount_x_wei_after_slippage = amount_x_wei - (amount_x_wei * int(self.task.slippage) / 100)
        amount_x_wei_after_slippage *= 1 - (dao_fee / 100000)

        swap_call = self.build_call(
            to_addr=self.router_contract.address,
            func_name='swap',
            call_data=[reserves_data['pool_id'],
                       self.i16(self.coin_y.contract_address),
                       amount_out_y_wei,
                       0,
                       amount_x_wei_after_slippage,
                       0]
        )

        calls = [approve_call, swap_call]

        return TransactionPayloadData(
            calls=calls,
            amount_x_decimals=amount_out_y_wei / 10 ** self.token_x_decimals,
            amount_y_decimals=amount_x_wei / 10 ** self.token_y_decimals
        )
