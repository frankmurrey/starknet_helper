from typing import TYPE_CHECKING

from starknet_py.net.client_models import Call
from loguru import logger

from modules.base import ModuleBase
from modules.dmail.random_generator import generate_random_profile
from src.schemas.dmail_profile import DmailProfileSchema
from contracts.dmail.main import DmailContracts
from src.schemas.action_models import ModuleExecutionResult
from utils.sha256 import sha256_hash

if TYPE_CHECKING:
    from src.schemas.tasks.dmail import DmailSendMailTask
    from src.schemas.wallet_data import WalletData


class DmailSendMail(ModuleBase):
    task: 'DmailSendMailTask'

    def __init__(
            self,
            account,
            task: 'DmailSendMailTask',
            wallet_data: 'WalletData',
    ):

        super().__init__(
            account=account,
            task=task,
            wallet_data=wallet_data,
        )

        self.task = task
        self.account = account

        self.dmail_contracts = DmailContracts()
        self.router_contract = self.get_contract(
            address=self.dmail_contracts.router_address,
            abi=self.dmail_contracts.router_abi,
            provider=account
        )
        self.profile: DmailProfileSchema = generate_random_profile()

    async def build_txn_payload_calls(self) -> list[Call]:
        """
        Build transaction payload calls
        :return:
        """
        to_email = sha256_hash(self.profile.email)[:31]
        theme = sha256_hash(self.profile.theme)[:31]
        mail_call = self.build_call(
            to_addr=self.router_contract.address,
            func_name='transaction',
            call_data=[
                to_email,
                theme
            ]
        )

        return [mail_call]

    async def send_txn(self) -> ModuleExecutionResult:
        """
        Send dmail transaction
        :return:
        """
        txn_payload_calls = await self.build_txn_payload_calls()
        if txn_payload_calls is None:
            self.log_error("Failed to build transaction payload data")
            return self.module_execution_result

        txn_info_message = f"Send mail (Dmail). Receiver: {self.profile.email}. Theme: {self.profile.theme}"

        txn_status = await self.simulate_and_send_transfer_type_transaction(
            account=self.account,
            calls=txn_payload_calls,
            txn_info_message=txn_info_message
        )

        return txn_status
