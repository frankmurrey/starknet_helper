from src.schemas.tasks import ZkLendSupplyTask
from src.schemas.tasks import ZkLendWithdrawTask
from src.schemas.tasks.virtual_task.base import VirtualTaskBase


class ZkLendSupplyVirtualTask(
    ZkLendSupplyTask,
    VirtualTaskBase,
):
    pass


class ZkLendWithdrawVirtualTask(
    ZkLendWithdrawTask,
    VirtualTaskBase,
):
    pass
