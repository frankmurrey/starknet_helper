from src.schemas.configs.transaction_settings_base import TransactionSettingsBase

from src import enums


class IdentityMintConfigSchema(TransactionSettingsBase):
    module_name: enums.ModuleName = enums.ModuleName.IDENTITY
    module_type: enums.ModuleType = enums.ModuleType.MINT
