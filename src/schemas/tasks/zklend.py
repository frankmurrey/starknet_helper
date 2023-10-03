from typing import Callable

from pydantic import Field

from src.schemas.tasks.base.supply import SupplyTaskBase
from src.schemas.tasks.base.withdraw import WithdrawTaskBase
from modules.zklend.supply import ZkLendSupply
from modules.zklend.withdraw import ZkLendWithdraw
from src import enums


class ZkLendSupplyTask(SupplyTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.ZKLEND
    module_type: enums.ModuleType = enums.ModuleType.SUPPLY
    module: Callable = Field(default=ZkLendSupply)


class ZkLendWithdrawTask(WithdrawTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.ZKLEND
    module_type: enums.ModuleType = enums.ModuleType.WITHDRAW
    module: Callable = Field(default=ZkLendWithdraw)
