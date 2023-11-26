from src.schemas.tasks import MySwapTask
from src.schemas.tasks import MySwapRemoveLiquidityTask
from src.schemas.tasks import MySwapAddLiquidityTask
from src.schemas.tasks.virtual_task.base import VirtualTaskBase


class MySwapVirtualTask(
    MySwapTask,
    VirtualTaskBase,
):
    pass


class MySwapRemoveLiquidityVirtualTask(
    MySwapRemoveLiquidityTask,
    VirtualTaskBase,
):
    pass


class MySwapAddLiquidityVirtualTask(
    MySwapAddLiquidityTask,
    VirtualTaskBase,
):
    pass
