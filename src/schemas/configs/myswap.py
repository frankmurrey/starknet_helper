from src.schemas.configs.transaction_settings_base import SwapSettingsBase
from src.schemas.configs.transaction_settings_base import AddLiquiditySettingsBase
from src.schemas.configs.transaction_settings_base import RemoveLiquiditySettingsBase

from src import enums


class MySwapConfigSchema(SwapSettingsBase):
    module_name: enums.ModuleName = enums.ModuleName.MY_SWAP
    module_type: enums.ModuleType = enums.ModuleType.SWAP


class MySwapAddLiquidityConfigSchema(AddLiquiditySettingsBase):
    module_name: enums.ModuleName = enums.ModuleName.MY_SWAP
    module_type: enums.ModuleType = enums.ModuleType.LIQUIDITY_ADD


class MySwapRemoveLiquidityConfigSchema(RemoveLiquiditySettingsBase):
    module_name: enums.ModuleName = enums.ModuleName.MY_SWAP
    module_type: enums.ModuleType = enums.ModuleType.LIQUIDITY_REMOVE
