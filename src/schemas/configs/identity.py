from src.schemas.configs.base import CommonSettingsBase


class IdentityMintConfigSchema(CommonSettingsBase):
    module_name: str = 'identity_mint'
