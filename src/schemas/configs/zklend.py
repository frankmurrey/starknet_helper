from src.schemas.configs.base import SupplySettingsBase
from src.schemas.configs.base import WithdrawSettingsBase

from src import enums


class ZkLendSupplyConfigSchema(SupplySettingsBase):
    module_name: enums.ModuleName = enums.ModuleName.ZKLEND
    module_type: enums.ModuleType = enums.ModuleType.SUPPLY


class ZkLendWithdrawConfigSchema(WithdrawSettingsBase):
    module_name: enums.ModuleName = enums.ModuleName.ZKLEND
    module_type: enums.ModuleType = enums.ModuleType.WITHDRAW
