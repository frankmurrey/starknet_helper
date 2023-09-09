from modules.base import StarkBase
from modules.dmail.random_generator import generate_random_profile
from src.schemas.configs.dmail import DmailSendMailConfigSchema
from src.schemas.dmail_profile import DmailProfileSchema
from contracts.dmail.main import DmailContracts


class DmailSendMail(StarkBase):
    config: DmailSendMailConfigSchema

    def __init__(
            self,
            account,
            config
    ):
        super().__init__(client=account.client)

        self.config = config
        self.account = account

        self.dmail_contracts = DmailContracts()
        self.router_contract = self.get_contract(address=self.dmail_contracts.router_address,
                                                 abi=self.dmail_contracts.router_abi,
                                                 provider=account)
        self.profile: DmailProfileSchema = generate_random_profile()

    async def build_txn_payload_calls(self):
        mail_call = self.build_call(
            to_addr=self.router_contract.address,
            func_name='transaction',
            call_data=[
                self.profile.email,
                self.profile.theme
            ]
        )

        return [mail_call]

    async def send_mail_txn(self):
        txn_payload_calls = await self.build_txn_payload_calls()
        if txn_payload_calls is None:
            return False

        txn_info_message = f"Send mail (Dmail). Receiver: {self.profile.email}. Theme: {self.profile.theme}"

        txn_status = await self.simulate_and_send_transfer_type_transaction(account=self.account,
                                                                            calls=txn_payload_calls,
                                                                            txn_info_message=txn_info_message,
                                                                            config=self.config)

        return txn_status



