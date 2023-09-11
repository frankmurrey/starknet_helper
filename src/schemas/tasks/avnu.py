from src.schemas.tasks.base.swap import SwapTaskBase
from src import enums


class AvnuSwapTask(SwapTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.AVNU
    module_type: enums.ModuleType = enums.ModuleType.SWAP
