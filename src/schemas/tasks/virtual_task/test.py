from src.schemas.tasks import TestTask
from src.schemas.tasks.virtual_task.base import VirtualTaskBase


class TestVirtualTask(
    TestTask,
    VirtualTaskBase,
):
    pass
