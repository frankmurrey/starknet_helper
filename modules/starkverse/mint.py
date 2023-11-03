from typing import TYPE_CHECKING
from typing import List

from starknet_py.net.account.account import Account
from starknet_py.net.client_models import Call

from modules.base import ModuleBase
from contracts.starkverse.main import StarkVerseContracts
from src.schemas.action_models import ModuleExecutionResult

if TYPE_CHECKING:
    from src.schemas.tasks.starkverse import StarkVersePublicMintTask


class PublicMint(ModuleBase):
    task: 'StarkVersePublicMintTask'
    account: Account

    def __init__(
            self,
            account,
            task: 'StarkVersePublicMintTask'
    ):
        super().__init__(
            account=account,
            task=task,
        )
        self.account = account
        self.task = task

        self.starkverse_contracts = StarkVerseContracts()
        self.router_contract = self.get_contract(
            address=self.starkverse_contracts.router_address,
            abi=self.starkverse_contracts.router_abi,
            provider=account
        )

    async def build_txn_calls(self) -> List[Call]:
        """
        Builds transaction payload data for the transaction.
        :return:
        """

        mint_call = self.build_call(
            to_addr=self.router_contract.address,
            func_name='publicMint',
            call_data=[
                self.account.address
            ]
        )

        return [mint_call]

    async def send_txn(self) -> ModuleExecutionResult:
        """
        Send the transaction.
        :return:
        """
        calls = await self.build_txn_calls()
        txn_info_message = f"Public Mint StarkVersse (1 NFT)"
        txn_status = await self.simulate_and_send_transfer_type_transaction(
            account=self.account,
            calls=calls,
            txn_info_message=txn_info_message
        )

        return txn_status


