from src.schemas.tasks import IdentityMintTask
from src.schemas.tasks.virtual_task.base import VirtualTaskBase


class IdentityMintVirtualTask(
    IdentityMintTask,
    VirtualTaskBase,
):
    pass
