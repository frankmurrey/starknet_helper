from typing import Union

from src.schemas.configs.base import CommonSettingsBase


class DeployArgentConfigSchema(CommonSettingsBase):
    module_name: str = 'deploy_argent'


class DeployBraavostConfigSchema(CommonSettingsBase):
    module_name: str = 'deploy_braavos'
