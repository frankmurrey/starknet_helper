from typing import Callable

from pydantic import Field

from src.schemas.tasks.base import TaskBase
from modules.deploy.deploy import Deploy
from src import enums


class DeployTask(TaskBase):
    module_name: enums.ModuleName = enums.ModuleName.DEPLOY
    module_type: enums.ModuleType = ""
    module: Callable = Field(default=Deploy)
