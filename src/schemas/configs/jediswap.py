from src.schemas.configs.transaction_settings_base import SwapSettingsBase
from src.schemas.configs.transaction_settings_base import AddLiquiditySettingsBase
from src.schemas.configs.transaction_settings_base import RemoveLiquiditySettingsBase

from src import enums


class JediSwapConfigSchema(SwapSettingsBase):
    module_name: enums.ModuleName = enums.ModuleName.JEDI_SWAP
    module_type: enums.ModuleType = enums.ModuleType.SWAP


class JediSwapAddLiquidityConfigSchema(AddLiquiditySettingsBase):
    module_name: enums.ModuleName = enums.ModuleName.JEDI_SWAP
    module_type: enums.ModuleType = enums.ModuleType.LIQUIDITY_ADD


class JediSwapRemoveLiquidityConfigSchema(RemoveLiquiditySettingsBase):
    module_name: enums.ModuleName = enums.ModuleName.JEDI_SWAP
    module_type: enums.ModuleType = enums.ModuleType.LIQUIDITY_REMOVE
