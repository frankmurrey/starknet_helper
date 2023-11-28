from src.schemas.tasks import TransferTask
from src.schemas.tasks.virtual_task.base import VirtualTaskBase


class TransferVirtualTask(
    TransferTask,
    VirtualTaskBase,
):
    pass
