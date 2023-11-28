from src.schemas.tasks import DmailSendMailTask
from src.schemas.tasks.virtual_task.base import VirtualTaskBase


class DmailSendMailVirtualTask(
    DmailSendMailTask,
    VirtualTaskBase,
):
    pass
