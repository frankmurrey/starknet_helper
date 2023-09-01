from src.schemas.configs.base import CommonSettingsBase

from src import enums


class IdentityMintConfigSchema(CommonSettingsBase):
    module_name: enums.ModuleName = enums.ModuleName.IDENTITY
    module_type: enums.ModuleType = enums.ModuleType.MINT
