from typing import Callable
from pydantic import Field

from src import enums
from src.schemas.tasks import TaskBase
from modules.zerius.mint import ZeriusMint


class ZeriusMintTask(TaskBase):
    module_type = enums.ModuleType.MINT
    module_name = enums.ModuleName.ZERIUS
    module: Callable = Field(default=ZeriusMint)

    use_reff: bool = True

    @property
    def action_info(self):
        return "Reff" if self.use_reff else "No Reff"
