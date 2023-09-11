from src.schemas.tasks.base import TaskBase

from src import enums


class IdentityMintTask(TaskBase):
    module_name: enums.ModuleName = enums.ModuleName.IDENTITY
    module_type: enums.ModuleType = enums.ModuleType.MINT
