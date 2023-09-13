from src.schemas.tasks.base import TaskBase

from src import enums


class DeployArgentTask(TaskBase):
    module_name: enums.ModuleName = enums.ModuleName.DEPLOY


class DeployBraavostTask(TaskBase):
    module_name: enums.ModuleName = enums.ModuleName.DEPLOY
