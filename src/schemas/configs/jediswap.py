from src.schemas.configs.base import SwapSettingsBase

from src import enums


class JediSwapConfigSchema(SwapSettingsBase):
    module_name: enums.ModuleName = enums.ModuleName.JEDI_SWAP
    module_type: enums.ModuleType = enums.ModuleType.SWAP
