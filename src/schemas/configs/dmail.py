from src.schemas.configs.transaction_settings_base import TransactionSettingsBase

from src import enums


class DmailSendMailConfigSchema(TransactionSettingsBase):
    module_name: enums.ModuleName = enums.ModuleName.DMAIL
    module_type: enums.ModuleType = enums.ModuleType.SEND_MAIL
    custom_mails: bool = False
    custom_messages: bool = False
