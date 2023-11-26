from src.schemas.tasks import SithSwapTask
from src.schemas.tasks import SithSwapRemoveLiquidityTask
from src.schemas.tasks import SithSwapAddLiquidityTask
from src.schemas.tasks.virtual_task.base import VirtualTaskBase


class SithSwapVirtualTask(
    SithSwapTask,
    VirtualTaskBase,
):
    pass


class SithSwapRemoveLiquidityVirtualTask(
    SithSwapRemoveLiquidityTask,
    VirtualTaskBase,
):
    pass


class SithSwapAddLiquidityVirtualTask(
    SithSwapAddLiquidityTask,
    VirtualTaskBase,
):
    pass
