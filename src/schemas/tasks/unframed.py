from typing import Callable
from pydantic import Field

from src import enums
from src.schemas.tasks.base.base import TaskBase
from modules.unframed.cancel_orders import CancelOrders


class UnframedCancelOrdersTask(TaskBase):
    module_name = enums.ModuleName.UNFRAMED
    module_type = enums.ModuleType.CANCEL_ORDER
    module: Callable = Field(default=CancelOrders)

