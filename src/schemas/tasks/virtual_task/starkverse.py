from src.schemas.tasks import StarkVersePublicMintTask
from src.schemas.tasks.virtual_task.base import VirtualTaskBase


class StarkVersePublicMintVirtualTask(
    StarkVersePublicMintTask,
    VirtualTaskBase
):
    pass
