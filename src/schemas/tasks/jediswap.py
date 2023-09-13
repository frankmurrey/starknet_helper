from typing import Callable

from src.schemas.tasks.base.swap import SwapTaskBase
from src.schemas.tasks.base.add_liquidity import AddLiquidityTaskBase
from src.schemas.tasks.base.remove_liquidity import RemoveLiquidityTaskBase
from modules.jediswap.swap import JediSwap
from modules.jediswap.liquidity import JediSwapAddLiquidity
from modules.jediswap.liquidity import JediSwapRemoveLiquidity

from src import enums


class JediSwapTask(SwapTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.JEDI_SWAP
    module_type: enums.ModuleType = enums.ModuleType.SWAP
    module: Callable = JediSwap


class JediSwapAddLiquidityTask(AddLiquidityTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.JEDI_SWAP
    module_type: enums.ModuleType = enums.ModuleType.LIQUIDITY_ADD
    module: Callable = JediSwapAddLiquidity


class JediSwapRemoveLiquidityTask(RemoveLiquidityTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.JEDI_SWAP
    module_type: enums.ModuleType = enums.ModuleType.LIQUIDITY_REMOVE
    module: Callable = JediSwapRemoveLiquidity
