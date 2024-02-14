from src.schemas.tasks import UnframedCancelOrdersTask
from src.schemas.tasks.virtual_task.base import VirtualTaskBase


class UnframedCancelOrdersVirtualTask(
    UnframedCancelOrdersTask,
    VirtualTaskBase,
):
    pass
