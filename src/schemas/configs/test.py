from src import enums

from src.schemas.configs.base import SwapSettingsBase


class TestConfigSchema(SwapSettingsBase):
    module_name: enums.ModuleName = enums.ModuleName.TEST
    module_type: enums.ModuleType = enums.ModuleType.TEST
