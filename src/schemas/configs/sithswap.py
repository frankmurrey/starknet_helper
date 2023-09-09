from src.schemas.configs.base import SwapSettingsBase
from src.schemas.configs.base import AddLiquiditySettingsBase
from src.schemas.configs.base import RemoveLiquiditySettingsBase

from src import enums


class SithSwapConfigSchema(SwapSettingsBase):
    module_name: enums.ModuleName = enums.ModuleName.SITHSWAP
    module_type: enums.ModuleType = enums.ModuleType.SWAP


class SithSwapAddLiquidityConfigSchema(AddLiquiditySettingsBase):
    module_name: enums.ModuleName = enums.ModuleName.SITHSWAP
    module_type: enums.ModuleType = enums.ModuleType.LIQUIDITY_ADD


class SithSwapRemoveLiquidityConfigSchema(RemoveLiquiditySettingsBase):
    module_name: enums.ModuleName = enums.ModuleName.SITHSWAP
    module_type: enums.ModuleType = enums.ModuleType.LIQUIDITY_REMOVE
