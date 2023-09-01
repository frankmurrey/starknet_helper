from src.schemas.configs.base import SwapSettingsBase

from src import enums


class MySwapConfigSchema(SwapSettingsBase):
    module_name: enums.ModuleName = enums.ModuleName.MY_SWAP
    module_type: enums.ModuleType = enums.ModuleType.SWAP
