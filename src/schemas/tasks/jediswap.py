from typing import Callable

from pydantic import Field

from src import enums
from src.schemas.tasks.base.swap import SwapTaskBase
from src.schemas.tasks.base.add_liquidity import AddLiquidityTaskBase
from src.schemas.tasks.base.remove_liquidity import RemoveLiquidityTaskBase
from modules.jediswap.swap import JediSwap
from modules.jediswap.liquidity import JediSwapAddLiquidity
from modules.jediswap.liquidity import JediSwapRemoveLiquidity


class JediSwapTask(SwapTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.JEDI_SWAP
    module_type: enums.ModuleType = enums.ModuleType.SWAP
    module: Callable = Field(default=JediSwap)


class JediSwapRemoveLiquidityTask(RemoveLiquidityTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.JEDI_SWAP
    module_type: enums.ModuleType = enums.ModuleType.LIQUIDITY_REMOVE
    module: Callable = Field(default=JediSwapRemoveLiquidity)


class JediSwapAddLiquidityTask(AddLiquidityTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.JEDI_SWAP
    module_type: enums.ModuleType = enums.ModuleType.LIQUIDITY_ADD
    module: Callable = Field(default=JediSwapAddLiquidity)
    reverse_action_task = Field(default=JediSwapRemoveLiquidityTask)

    class Config:
        arbitrary_types_allowed = True
