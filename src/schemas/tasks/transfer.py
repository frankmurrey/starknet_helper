from typing import Callable

from pydantic import Field

from modules.transfer.transfer import Transfer
from src.schemas.tasks.base.transfer import TransferTaskBase
from src import enums


class TransferTask(TransferTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.TRANSFER
    module_type: enums.ModuleType = enums.ModuleType.SEND
    module: Callable = Field(default=Transfer)
