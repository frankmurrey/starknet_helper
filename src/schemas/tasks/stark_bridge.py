from typing import Callable
from pydantic import Field

from src.schemas.tasks.base.bridge import BridgeTaskBase
from src import enums
from modules.stark_bridge.bridge import StarkBridge


class StarkBridgeTask(BridgeTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.STARK_BRIDGE
    module_type: enums.ModuleType = enums.ModuleType.BRIDGE
    module: Callable = Field(default=StarkBridge)
