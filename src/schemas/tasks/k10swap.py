from src.schemas.tasks.base.swap import SwapTaskBase

from src import enums


class K10SwapTask(SwapTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.K10SWAP
    module_type: enums.ModuleType = enums.ModuleType.SWAP

