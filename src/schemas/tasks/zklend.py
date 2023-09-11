from src.schemas.tasks.base.supply import SupplyTaskBase
from src.schemas.tasks.base.withdraw import WithdrawTaskBase

from src import enums


class ZkLendSupplyTask(SupplyTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.ZKLEND
    module_type: enums.ModuleType = enums.ModuleType.SUPPLY


class ZkLendWithdrawTask(WithdrawTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.ZKLEND
    module_type: enums.ModuleType = enums.ModuleType.WITHDRAW
