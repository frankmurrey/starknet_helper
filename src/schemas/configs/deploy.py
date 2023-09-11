from src.schemas.configs.transaction_settings_base import TransactionSettingsBase

from src import enums


class DeployArgentConfigSchema(TransactionSettingsBase):
    module_name: enums.ModuleName = enums.ModuleName.DEPLOY
    module_type: enums.PrivateKeyType = enums.PrivateKeyType.argent


class DeployBraavostConfigSchema(TransactionSettingsBase):
    module_name: enums.ModuleName = enums.ModuleName.DEPLOY
    module_type: enums.PrivateKeyType = enums.PrivateKeyType.braavos
