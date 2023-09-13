from typing import Callable

from pydantic import Field

from src.schemas.tasks.base import TaskBase
from modules.dmail.send_mail import DmailSendMail
from src import enums


class DmailSendMailTask(TaskBase):
    module_name: enums.ModuleName = enums.ModuleName.DMAIL
    module_type: enums.ModuleType = enums.ModuleType.SEND_MAIL
    custom_mails: bool = False
    custom_messages: bool = False
    module: Callable = Field(default=DmailSendMail)
