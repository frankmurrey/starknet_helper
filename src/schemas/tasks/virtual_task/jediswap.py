from src.schemas.tasks import JediSwapTask
from src.schemas.tasks import JediSwapRemoveLiquidityTask
from src.schemas.tasks import JediSwapAddLiquidityTask
from src.schemas.tasks.virtual_task.base import VirtualTaskBase


class JediSwapVirtualTask(
    JediSwapTask,
    VirtualTaskBase,
):
    pass


class JediSwapRemoveLiquidityVirtualTask(
    JediSwapRemoveLiquidityTask,
    VirtualTaskBase,
):
    pass


class JediSwapAddLiquidityVirtualTask(
    JediSwapAddLiquidityTask,
    VirtualTaskBase,
):
    pass
