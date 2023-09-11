from src import enums

from src.schemas.tasks.base.swap import SwapTaskBase


class TestTask(SwapTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.TEST
    module_type: enums.ModuleType = enums.ModuleType.TEST
