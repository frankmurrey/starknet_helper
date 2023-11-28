from src.schemas.tasks import OrbiterBridgeTask
from src.schemas.tasks.virtual_task.base import VirtualTaskBase


class OrbiterBridgeVirtualTask(
    OrbiterBridgeTask,
    VirtualTaskBase,
):
    pass
