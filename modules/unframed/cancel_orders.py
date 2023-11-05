import random

from typing import TYPE_CHECKING

from starknet_py.net.client_models import Call

from modules.base import ModuleBase
from contracts.unframed.main import UnframedContracts
from src.schemas.action_models import ModuleExecutionResult

if TYPE_CHECKING:
    from src.schemas.tasks.unframed import UnframedCancelOrdersTask


class CancelOrders(ModuleBase):
    task: 'UnframedCancelOrdersTask'

    def __init__(
            self,
            account,
            task: 'UnframedCancelOrdersTask'
    ):
        super().__init__(
            account=account,
            task=task,
        )

        self.account = account
        self.task = task

        self.unframed_contracts = UnframedContracts()
        self.router_contract = self.get_contract(
            address=self.unframed_contracts.router_address,
            abi=self.unframed_contracts.router_abi,
            provider=account
        )

    def generate_random_hex(self) -> str:
        return '0x' + ''.join(random.choice('0123456789abcdef') for _ in range(62))

    async def build_txn_payload_calls(self) -> list[Call]:
        """
        Build the transaction payload calls for the identity mint transaction.
        :return:
        """
        random_nonce = self.generate_random_hex()

        cancel_call = self.build_call(
            to_addr=self.router_contract.address,
            func_name='cancel_orders',
            call_data=[
                1,
                self.i16(random_nonce),
            ]
        )

        return [cancel_call]

    async def send_txn(self) -> ModuleExecutionResult:
        """
        Send the identity mint transaction.
        :return:
        """
        txn_payload_calls = await self.build_txn_payload_calls()
        if txn_payload_calls is None:
            self.module_execution_result.execution_info = f"Failed to build transaction payload calls"
            return self.module_execution_result

        txn_info_message = f"Unframed - cancel orders"

        txn_status = await self.simulate_and_send_transfer_type_transaction(
            account=self.account,
            calls=txn_payload_calls,
            txn_info_message=txn_info_message
        )

        return txn_status
