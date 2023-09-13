from typing import Callable

from src.schemas.tasks.base.swap import SwapTaskBase
from src import enums
from modules.avnu.swap import AvnuSwap


class AvnuSwapTask(SwapTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.AVNU
    module_type: enums.ModuleType = enums.ModuleType.SWAP
    module: Callable = AvnuSwap
