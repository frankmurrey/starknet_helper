from typing import TYPE_CHECKING, Union, List

from loguru import logger
from starknet_py.net.client_models import Call

from modules.base import ModuleBase
from contracts.tokens.main import Tokens
from contracts.zklend.main import ZkLendContracts
from src.schemas.action_models import ModuleExecutionResult

if TYPE_CHECKING:
    from src.schemas.tasks.zklend import ZkLendWithdrawTask
    from src.schemas.wallet_data import WalletData


class ZkLendWithdraw(ModuleBase):
    task: 'ZkLendWithdrawTask'

    def __init__(
            self,
            account,
            task: 'ZkLendWithdrawTask',
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

        self.coin_x = self.tokens.get_by_name(self.task.coin_to_withdraw)
        self.coin_zx = self.tokens.get_by_name(f"z{self.coin_x.symbol.lower()}")

        self.amount_out_decimals = None

    async def build_txn_payload_calls(self) -> Union[List[Call], None]:
        """
        Build transaction payload calls
        :return:
        """
        supplied_balance_wei = await self.get_token_balance(
            token_address=self.coin_zx.contract_address,
            account=self.account
        )
        if supplied_balance_wei == 0:
            self.log_error(f"Wallet {self.coin_zx.symbol.upper()} balance = 0, nothing to withdraw")
            return None

        withdraw_call = self.build_call(
            to_addr=self.router_contract.address,
            func_name="withdraw_all",
            call_data=[self.i16(self.coin_x.contract_address)]
        )

        token_decimals = await self.get_token_decimals(
            contract_address=self.coin_zx.contract_address,
            abi=self.coin_zx.abi,
            provider=self.account
        )
        if token_decimals is None:
            self.log_error(f"Failed to get {self.coin_zx.symbol.upper()} decimals")
            return None

        self.amount_out_decimals = supplied_balance_wei / 10 ** token_decimals

        return [withdraw_call]

    async def send_txn(self) -> ModuleExecutionResult:
        """
        Send the transaction.
        :return:
        """
        txn_payload_calls = await self.build_txn_payload_calls()
        if txn_payload_calls is None:
            self.log_error(f"Failed to build transaction payload calls")
            return self.module_execution_result

        txn_info_message = f"Withdraw (ZkLend) | {round(self.amount_out_decimals, 4)} ({self.coin_x.symbol.upper()})."

        txn_status = await self.simulate_and_send_transfer_type_transaction(
            account=self.account,
            calls=txn_payload_calls,
            txn_info_message=txn_info_message
        )

        return txn_status
