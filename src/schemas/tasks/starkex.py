from typing import Callable

from pydantic import Field

from src import enums
from src.schemas.tasks.base.swap import SwapTaskBase
from src.schemas.tasks.base.add_liquidity import AddLiquidityTaskBase
from src.schemas.tasks.base.remove_liquidity import RemoveLiquidityTaskBase
from modules.starkex.swap import StarkExSwap


class StarkExSwapTask(SwapTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.STARKEX
    module_type: enums.ModuleType = enums.ModuleType.SWAP
    module: Callable = Field(default=StarkExSwap)


class StarkExAddLiquidityTask(AddLiquidityTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.STARKEX
    module_type: enums.ModuleType = enums.ModuleType.LIQUIDITY_ADD
    # TODO add module


class StarkExRemoveLiquidityTask(RemoveLiquidityTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.STARKEX
    module_type: enums.ModuleType = enums.ModuleType.LIQUIDITY_REMOVE
    # TODO add module