from typing import Callable

from pydantic import Field

from src import enums
from src.schemas.tasks.base.swap import SwapTaskBase
from modules.fibrous.swap import FibrousSwap


class FibrousSwapTask(SwapTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.FIBROUS
    module_type: enums.ModuleType = enums.ModuleType.SWAP
    module: Callable = Field(default=FibrousSwap)
