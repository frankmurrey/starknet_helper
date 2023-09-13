from typing import Callable

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
    module: Callable = MySwap


class MySwapAddLiquidityTask(AddLiquidityTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.MY_SWAP
    module_type: enums.ModuleType = enums.ModuleType.LIQUIDITY_ADD
    module: Callable = MySwapAddLiquidity


class MySwapRemoveLiquidityTask(RemoveLiquidityTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.MY_SWAP
    module_type: enums.ModuleType = enums.ModuleType.LIQUIDITY_REMOVE
    module: Callable = MySwapRemoveLiquidity
