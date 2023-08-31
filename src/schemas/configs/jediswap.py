from typing import Union
from src.schemas.configs.base import SwapSettingsBase

from src import enums


class JediSwapConfigSchema(SwapSettingsBase):
    module_name: str = 'jediswap_swap'
    module_type: enums.ModuleType = enums.ModuleType.SWAP
