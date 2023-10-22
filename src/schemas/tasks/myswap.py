from typing import Callable
from pydantic import Field

from src.schemas.tasks.base.swap import SwapTaskBase
from src.schemas.tasks.base.add_liquidity import AddLiquidityTaskBase
from src.schemas.tasks.base.remove_liquidity import RemoveLiquidityTaskBase
from modules.myswap.swap import MySwap
from modules.myswap.liquidity import MySwapAddLiquidity
from modules.myswap.liquidity import MySwapRemoveLiquidity
from src import enums


class MySwapTask(SwapTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.MY_SWAP
    module_type: enums.ModuleType = enums.ModuleType.SWAP
    module: Callable = Field(default=MySwap)


class MySwapRemoveLiquidityTask(RemoveLiquidityTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.MY_SWAP
    module_type: enums.ModuleType = enums.ModuleType.LIQUIDITY_REMOVE
    module: Callable = Field(default=MySwapRemoveLiquidity)


class MySwapAddLiquidityTask(AddLiquidityTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.MY_SWAP
    module_type: enums.ModuleType = enums.ModuleType.LIQUIDITY_ADD
    module: Callable = Field(default=MySwapAddLiquidity)
    reverse_action_task = Field(default=MySwapRemoveLiquidityTask)

    class Config:
        arbitrary_types_allowed = True

