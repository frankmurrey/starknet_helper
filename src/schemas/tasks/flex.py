from typing import Callable
from pydantic import Field

from src import enums
from src.schemas.tasks.base.base import TaskBase
from modules.flex.cancel_orders import CancelOrders


class FlexCancelOrdersTask(TaskBase):
    module_name = enums.ModuleName.FLEX
    module_type = enums.ModuleType.CANCEL_ORDER
    module: Callable = Field(default=CancelOrders)

