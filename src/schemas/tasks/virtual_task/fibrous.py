from src.schemas.tasks import FibrousSwapTask
from src.schemas.tasks.virtual_task.base import VirtualTaskBase


class FibrousSwapVirtualTask(
    FibrousSwapTask,
    VirtualTaskBase,
):
    pass
