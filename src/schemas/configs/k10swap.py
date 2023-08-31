from src.schemas.configs.base import SwapSettingsBase


class K10SwapConfigSchema(SwapSettingsBase):
    module_name: str = 'k10swap_swap'

