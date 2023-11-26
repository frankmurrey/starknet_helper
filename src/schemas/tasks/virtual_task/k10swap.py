from src.schemas.tasks import K10SwapTask
from src.schemas.tasks import K10SwapRemoveLiquidityTask
from src.schemas.tasks import K10SwapAddLiquidityTask
from src.schemas.tasks.virtual_task.base import VirtualTaskBase


class K10SwapVirtualTask(
    K10SwapTask,
    VirtualTaskBase,
):
    pass


class K10SwapRemoveLiquidityVirtualTask(
    K10SwapRemoveLiquidityTask,
    VirtualTaskBase,
):
    pass


class K10SwapAddLiquidityVirtualTask(
    K10SwapAddLiquidityTask,
    VirtualTaskBase,
):
    pass

