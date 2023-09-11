from src.schemas.tasks.base import TaskBase

from src import enums


class DeployArgentTask(TaskBase):
    module_name: enums.ModuleName = enums.ModuleName.DEPLOY
    module_type: enums.PrivateKeyType = enums.PrivateKeyType.argent


class DeployBraavostTask(TaskBase):
    module_name: enums.ModuleName = enums.ModuleName.DEPLOY
    module_type: enums.PrivateKeyType = enums.PrivateKeyType.braavos
