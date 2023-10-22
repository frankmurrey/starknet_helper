from typing import Callable
from pydantic import Field

from src.schemas.tasks.base.bridge import BridgeTaskBase
from src import enums
from modules.orbiter.bridge import OrbiterBridge


class OrbiterBridgeTask(BridgeTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.ORBITER
    module_type: enums.ModuleType = enums.ModuleType.BRIDGE
    module: Callable = Field(default=OrbiterBridge)
