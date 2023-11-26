from src.schemas.tasks import ZeriusMintTask
from src.schemas.tasks.virtual_task.base import VirtualTaskBase


class ZeriusMintVirtualTask(
    ZeriusMintTask,
    VirtualTaskBase,
):
    pass
