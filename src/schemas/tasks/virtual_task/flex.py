from src.schemas.tasks import FlexCancelOrdersTask
from src.schemas.tasks.virtual_task.base import VirtualTaskBase


class FlexCancelOrdersVirtualTask(
    FlexCancelOrdersTask,
    VirtualTaskBase,
):
    pass
