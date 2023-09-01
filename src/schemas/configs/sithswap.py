from src.schemas.configs.base import SwapSettingsBase

from src import enums


class SithSwapConfigSchema(SwapSettingsBase):
    module_name: enums.ModuleName = enums.ModuleName.SITHSWAP
    module_type: enums.ModuleType = enums.ModuleType.SWAP
