from src.schemas.configs.base import SwapSettingsBase


class SithSwapConfigSchema(SwapSettingsBase):
    module_name: str = 'sithswap_swap'
