import random
from typing import TYPE_CHECKING

from starknet_py.net.client_models import Call
from loguru import logger

from modules.base import ModuleBase
from contracts.flex.main import FlexContracts
from src.schemas.action_models import ModuleExecutionResult

if TYPE_CHECKING:
    from src.schemas.tasks.flex import FlexCancelOrdersTask
    from src.schemas.wallet_data import WalletData


class CancelOrders(ModuleBase):
    task: 'FlexCancelOrdersTask'

    def __init__(
            self,
            account,
            task: 'FlexCancelOrdersTask',
            wallet_data: 'WalletData',
    ):
        super().__init__(
            account=account,
            task=task,
            wallet_data=wallet_data,
        )

        self.account = account
        self.task = task

        self.flex_contracts = FlexContracts()
        self.router_contract = self.get_contract(
            address=self.flex_contracts.router_address,
            abi=self.flex_contracts.router_abi,
            provider=account
        )

    async def build_txn_payload_data(self) -> list[Call]:
        """
        Build the transaction payload calls for the identity mint transaction.
        :return:
        """

        cancel_call = self.build_call(
            to_addr=self.router_contract.address,
            func_name='cancelMakerOrder',
            call_data=[
                random.choice([20, 21]),
            ]
        )

        return [cancel_call]

    async def send_txn(self) -> ModuleExecutionResult:
        """
        Send the identity mint transaction.
        :return:
        """
        txn_payload_data = await self.build_txn_payload_data()

        txn_info_message = f"Flex - cancel maker order"

        txn_status = await self.simulate_and_send_transfer_type_transaction(
            account=self.account,
            calls=txn_payload_data,
            txn_info_message=txn_info_message
        )

        return txn_status
