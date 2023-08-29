from typing import Union

from src.schemas.configs.base import CommonSettingsBase


class DeployConfigSchema(CommonSettingsBase):
    module_name: str = 'deploy'
    provider: Union[str, None] = "argent"
