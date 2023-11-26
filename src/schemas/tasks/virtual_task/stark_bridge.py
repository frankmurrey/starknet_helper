from src.schemas.tasks import StarkBridgeTask
from src.schemas.tasks.virtual_task.base import VirtualTaskBase


class StarkBridgeVirtualTask(
    StarkBridgeTask,
    VirtualTaskBase
):
    pass
