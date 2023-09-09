from src.schemas.configs.base import SwapSettingsBase

from src import enums


class K10SwapConfigSchema(SwapSettingsBase):
    module_name: enums.ModuleName = enums.ModuleName.K10SWAP
    module_type: enums.ModuleType = enums.ModuleType.SWAP

