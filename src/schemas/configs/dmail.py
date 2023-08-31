from src.schemas.configs.base import CommonSettingsBase


class DmailSendMailConfigSchema(CommonSettingsBase):
    module_name: str = 'dmail_send_mail'
    custom_mails: bool = False
    custom_messages: bool = False
