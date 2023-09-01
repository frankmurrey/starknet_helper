from src.schemas.configs.base import SwapSettingsBase

from src import enums


class AvnuSwapConfigSchema(SwapSettingsBase):
    module_name: enums.ModuleName = enums.ModuleName.AVNU
    module_type: enums.ModuleType = enums.ModuleType.SWAP
