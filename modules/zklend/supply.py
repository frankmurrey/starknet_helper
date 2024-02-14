import random
from typing import TYPE_CHECKING, Union, List

from loguru import logger
from starknet_py.net.client_models import Call

from modules.base import ModuleBase
from contracts.tokens.main import Tokens
from contracts.zklend.main import ZkLendContracts
from src.schemas.action_models import ModuleExecutionResult

if TYPE_CHECKING:
    from src.schemas.tasks.zklend import ZkLendSupplyTask
    from src.schemas.wallet_data import WalletData


class ZkLendSupply(ModuleBase):
    task: 'ZkLendSupplyTask'

    def __init__(
            self,
            account,
            task: 'ZkLendSupplyTask',
            wallet_data: 'WalletData',
    ):
        super().__init__(
            account=account,
            task=task,
            wallet_data=wallet_data,
        )

        self.task = task
        self.account = account

        self.tokens = Tokens()
        self.zk_lend_contracts = ZkLendContracts()
        self.router_contract = self.get_contract(
            address=self.zk_lend_contracts.router_address,
            abi=self.zk_lend_contracts.router_abi,
            provider=account
        )

        self.coin_x = self.tokens.get_by_name(self.task.coin_to_supply)

        self.amount_out_decimals = None

    async def get_amount_out_from_balance(self) -> Union[int, None]:
        """
        Get amount out of balance
        :return:
        """
        wallet_token_balance_wei = await self.get_token_balance(
            token_address=self.coin_x.contract_address,
            account=self.account
        )

        if wallet_token_balance_wei == 0:
            self.log_error(f"Wallet {self.coin_x.symbol.upper()} balance = 0")
            return None

        token_x_decimals = await self.get_token_decimals(
            contract_address=self.coin_x.contract_address,
            abi=self.coin_x.abi,
            provider=self.account
        )
        if token_x_decimals is None:
            self.log_error(f"Failed to get {self.coin_x.symbol.upper()} decimals")
            return None

        wallet_token_balance_decimals = wallet_token_balance_wei / 10 ** token_x_decimals

        if self.task.use_all_balance is True:
            amount_out_wei = wallet_token_balance_wei

        elif self.task.send_percent_balance is True:
            percent = random.randint(int(self.task.min_amount_out), int(self.task.max_amount_out)) / 100
            amount_out_wei = int(wallet_token_balance_wei * percent)

        elif wallet_token_balance_decimals < self.task.max_amount_out:
            amount_out_wei = self.get_random_amount_out_of_token(
                min_amount=self.task.min_amount_out,
                max_amount=wallet_token_balance_decimals,
                decimals=token_x_decimals
            )

        else:
            amount_out_wei = self.get_random_amount_out_of_token(
                min_amount=self.task.min_amount_out,
                max_amount=self.task.max_amount_out,
                decimals=token_x_decimals
            )

        self.amount_out_decimals = amount_out_wei / 10 ** token_x_decimals

        return int(amount_out_wei)

    def build_deposit_call(
            self,
            amount_out_wei: int
    ) -> Call:
        """
        Build deposit call
        :param amount_out_wei:
        :return:
        """
        deposit_call = self.build_call(
            to_addr=self.router_contract.address,
            func_name='deposit',
            call_data=[
                self.i16(self.coin_x.contract_address),
                amount_out_wei
            ]
        )

        return deposit_call

    def build_enable_collateral_call(self) -> Call:
        """
        Build enable collateral call
        :return:
        """
        enable_collateral_call = self.build_call(
            to_addr=self.router_contract.address,
            func_name='enable_collateral',
            call_data=[
                self.i16(self.coin_x.contract_address)
            ]
        )

        return enable_collateral_call

    async def build_txn_payload_calls(self) -> Union[List[Call], None]:
        """
        Build transaction payload calls
        :return:
        """
        amount_out_wei = await self.get_amount_out_from_balance()
        if amount_out_wei is None:
            self.log_error(f"Error while calculating amount out for {self.coin_x.symbol.upper()}")
            return None

        approve_call = self.build_token_approve_call(
            token_addr=self.coin_x.contract_address,
            spender=hex(self.router_contract.address),
            amount_wei=int(amount_out_wei)
        )

        deposit_call = self.build_deposit_call(amount_out_wei=amount_out_wei)

        calls = [approve_call, deposit_call]

        if self.task.enable_collateral is True:
            enable_collateral_call = self.build_enable_collateral_call()
            calls.append(enable_collateral_call)

        return calls

    async def send_txn(self) -> ModuleExecutionResult:
        """
        Send supply transaction
        :return:
        """
        txn_payload_calls = await self.build_txn_payload_calls()
        if txn_payload_calls is None:
            self.log_error(f"Failed to build transaction payload calls")
            return self.module_execution_result

        txn_info_message = (
            f"Supply (ZkLend) | {round(self.amount_out_decimals, 4)} ({self.coin_x.symbol.upper()}). "
            f"Enable collateral: {self.task.enable_collateral}."
        )

        txn_status = await self.simulate_and_send_transfer_type_transaction(
            account=self.account,
            calls=txn_payload_calls,
            txn_info_message=txn_info_message
        )

        return txn_status
