from src import enums

from src.schemas.configs.transaction_settings_base import SwapSettingsBase


class TestConfigSchema(SwapSettingsBase):
    module_name: enums.ModuleName = enums.ModuleName.TEST
    module_type: enums.ModuleType = enums.ModuleType.TEST
