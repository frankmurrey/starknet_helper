from typing import Callable

from src.schemas.tasks.base import TaskBase
from modules.deploy.deploy import Deploy

from src import enums


class DeployTask(TaskBase):
    module_name: enums.ModuleName = enums.ModuleName.DEPLOY
    module_type: enums.ModuleType = ""
    module: Callable = Deploy
