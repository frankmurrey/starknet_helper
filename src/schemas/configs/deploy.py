from src.schemas.configs.transaction_settings_base import CommonSettingsBase

from src import enums


class DeployArgentConfigSchema(CommonSettingsBase):
    module_name: enums.ModuleName = enums.ModuleName.DEPLOY
    module_type: enums.PrivateKeyType = enums.PrivateKeyType.argent


class DeployBraavostConfigSchema(CommonSettingsBase):
    module_name: enums.ModuleName = enums.ModuleName.DEPLOY
    module_type: enums.PrivateKeyType = enums.PrivateKeyType.braavos
