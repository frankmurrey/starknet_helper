from typing import Callable

from pydantic import Field

from src.schemas.tasks.base.swap import SwapTaskBase
from modules.k10swap.swap import K10Swap
from src import enums


class K10SwapTask(SwapTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.K10SWAP
    module_type: enums.ModuleType = enums.ModuleType.SWAP
    module: Callable = Field(default=K10Swap)

