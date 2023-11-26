from src.schemas.tasks import AvnuSwapTask
from src.schemas.tasks.virtual_task.base import VirtualTaskBase


class AvnuSwapVirtualTask(
    AvnuSwapTask,
    VirtualTaskBase,
):
    pass
