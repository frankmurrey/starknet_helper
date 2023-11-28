from src.schemas.tasks import StarkExSwapTask
from src.schemas.tasks import StarkExAddLiquidityTask
from src.schemas.tasks import StarkExRemoveLiquidityTask
from src.schemas.tasks.virtual_task.base import VirtualTaskBase


class StarkExSwapVirtualTask(
    StarkExSwapTask,
    VirtualTaskBase,
):
    pass


class StarkExAddLiquidityVirtualTask(
    StarkExAddLiquidityTask,
    VirtualTaskBase,
):
    pass


class StarkExRemoveLiquidityVirtualTask(
    StarkExRemoveLiquidityTask,
    VirtualTaskBase,
):
    pass
