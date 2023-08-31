from src.schemas.configs.base import SwapSettingsBase

from src import enums


class JediSwapConfigSchema(SwapSettingsBase):
    module_name: str = 'jediswap'
    module_type: enums.ModuleType = enums.ModuleType.SWAP
