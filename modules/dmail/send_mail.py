from modules.base import StarkBase
from src.schemas.configs.dmail import DmailSendMailConfigSchema
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

    def build_txn_payload_calls(self):
        pass

