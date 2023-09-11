from src.schemas.tasks.base.swap import SwapTaskBase
from src.schemas.tasks.base.add_liquidity import AddLiquidityTaskBase
from src.schemas.tasks.base.remove_liquidity import RemoveLiquidityTaskBase

from src import enums


class MySwapTask(SwapTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.MY_SWAP
    module_type: enums.ModuleType = enums.ModuleType.SWAP


class MySwapAddLiquidityTask(AddLiquidityTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.MY_SWAP
    module_type: enums.ModuleType = enums.ModuleType.LIQUIDITY_ADD


class MySwapRemoveLiquidityTask(RemoveLiquidityTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.MY_SWAP
    module_type: enums.ModuleType = enums.ModuleType.LIQUIDITY_REMOVE
