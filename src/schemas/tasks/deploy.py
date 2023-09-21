from typing import Callable

from pydantic import Field

from src.schemas.tasks.base import TaskBase
from modules.deploy.deploy import Deploy
from modules.deploy.upgrade import Upgrade
from src import enums


class DeployTask(TaskBase):
    module_name: enums.ModuleName = enums.ModuleName.DEPLOY
    module_type: enums.ModuleType = enums.ModuleType.DEPLOY
    module: Callable = Field(default=Deploy)


class UpgradeTask(TaskBase):
    module_name: enums.ModuleName = enums.ModuleName.UPGRADE
    module_type: enums.ModuleType = enums.ModuleType.UPGRADE
    module: Callable = Field(default=Upgrade)
