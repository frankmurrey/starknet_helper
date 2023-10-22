from typing import Callable
from pydantic import Field

from src.schemas.tasks.base.swap import SwapTaskBase
from src.schemas.tasks.base.add_liquidity import AddLiquidityTaskBase
from src.schemas.tasks.base.remove_liquidity import RemoveLiquidityTaskBase
from modules.sithswap.swap import SithSwap
from modules.sithswap.liquidity import SithSwapAddLiquidity
from modules.sithswap.liquidity import SithSwapRemoveLiquidity
from src import enums


class SithSwapTask(SwapTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.SITHSWAP
    module_type: enums.ModuleType = enums.ModuleType.SWAP
    module: Callable = Field(default=SithSwap)


class SithSwapRemoveLiquidityTask(RemoveLiquidityTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.SITHSWAP
    module_type: enums.ModuleType = enums.ModuleType.LIQUIDITY_REMOVE
    module: Callable = Field(default=SithSwapRemoveLiquidity)


class SithSwapAddLiquidityTask(AddLiquidityTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.SITHSWAP
    module_type: enums.ModuleType = enums.ModuleType.LIQUIDITY_ADD
    module: Callable = Field(default=SithSwapAddLiquidity)
    reverse_action_task = Field(default=SithSwapRemoveLiquidityTask)

    class Config:
        arbitrary_types_allowed = True
