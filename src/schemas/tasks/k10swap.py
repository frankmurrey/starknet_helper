from typing import Callable

from pydantic import Field

from src.schemas.tasks.base.swap import SwapTaskBase
from src.schemas.tasks.base.add_liquidity import AddLiquidityTaskBase
from src.schemas.tasks.base.remove_liquidity import RemoveLiquidityTaskBase
from modules.k10swap.swap import K10Swap
from modules.k10swap.liquidity import K10SwapAddLiquidity
from modules.k10swap.liquidity import K10SwapRemoveLiquidity
from src import enums


class K10SwapTask(SwapTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.K10SWAP
    module_type: enums.ModuleType = enums.ModuleType.SWAP
    module: Callable = Field(default=K10Swap)


class K10SwapRemoveLiquidityTask(RemoveLiquidityTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.K10SWAP
    module_type: enums.ModuleType = enums.ModuleType.LIQUIDITY_REMOVE
    module: Callable = Field(default=K10SwapRemoveLiquidity)


class K10SwapAddLiquidityTask(AddLiquidityTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.K10SWAP
    module_type: enums.ModuleType = enums.ModuleType.LIQUIDITY_ADD
    module: Callable = Field(default=K10SwapAddLiquidity)
    reverse_action_task = Field(default=K10SwapRemoveLiquidityTask)

    class Config:
        arbitrary_types_allowed = True

