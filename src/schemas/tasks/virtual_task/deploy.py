from src.schemas.tasks import DeployTask, UpgradeTask
from src.schemas.tasks.virtual_task.base import VirtualTaskBase


class DeployVirtualTask(
    DeployTask,
    VirtualTaskBase,
):
    pass


class UpgradeVirtualTask(
    UpgradeTask,
    VirtualTaskBase,
):
    pass
