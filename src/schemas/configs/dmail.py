from src.schemas.configs.base import CommonSettingsBase

from src import enums


class DmailSendMailConfigSchema(CommonSettingsBase):
    module_name: enums.ModuleName = enums.ModuleName.DMAIL
    module_type: enums.ModuleType = enums.ModuleType.SEND_MAIL
    custom_mails: bool = False
    custom_messages: bool = False
