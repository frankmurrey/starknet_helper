from src.schemas.tasks.base.swap import SwapTaskBase
from src.schemas.tasks.base.add_liquidity import AddLiquidityTaskBase
from src.schemas.tasks.base.remove_liquidity import RemoveLiquidityTaskBase

from src import enums


class JediSwapTask(SwapTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.JEDI_SWAP
    module_type: enums.ModuleType = enums.ModuleType.SWAP


class JediSwapAddLiquidityTask(AddLiquidityTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.JEDI_SWAP
    module_type: enums.ModuleType = enums.ModuleType.LIQUIDITY_ADD


class JediSwapRemoveLiquidityTask(RemoveLiquidityTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.JEDI_SWAP
    module_type: enums.ModuleType = enums.ModuleType.LIQUIDITY_REMOVE
