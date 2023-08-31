from src.schemas.configs.base import SwapSettingsBase


class MySwapConfigSchema( SwapSettingsBase):
    module_name: str = 'myswap_swap'
