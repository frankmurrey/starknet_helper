from typing import Union, Callable, Optional

from pydantic import BaseModel
from pydantic import validator

from utlis import validation
from src import enums


class TaskBase(BaseModel):
    module_type: enums.ModuleType
    module_name: enums.ModuleName
    module: Optional[Callable]

    max_fee: int
    forced_gas_limit: bool = False

    # GLOBALS
    wait_for_receipt: bool = False
    txn_wait_timeout_sec: int = 60

    reverse_action: bool = False

    min_delay_sec: float = 40
    max_delay_sec: float = 80

    test_mode: bool = True

    @property
    def action_info(self):
        return f""

    @validator("max_fee", pre=True)
    def validate_max_fee_pre(cls, value):

        value = validation.get_converted_to_int(value, "Max Fee")
        value = validation.get_positive(value, "Max Fee", include_zero=False)

        return value

    @validator("txn_wait_timeout_sec", pre=True)
    def validate_txn_wait_timeout_sec_pre(cls, value, values):

        if not values["wait_for_receipt"]:
            return 0

        value = validation.get_converted_to_float(value, "Txn Wait Timeout")
        value = validation.get_positive(value, "Txn Wait Timeout")

        return value

    @validator("min_delay_sec", pre=True)
    def validate_min_delay_sec_pre(cls, value):

        value = validation.get_converted_to_float(value, "Min Delay")
        value = validation.get_positive(value, "Min Delay")

        return value

    @validator("max_delay_sec", pre=True)
    def validate_max_delay_sec_pre(cls, value, values):

        value = validation.get_converted_to_float(value, "Max Delay")
        value = validation.get_greater(value, values["min_delay_sec"], "Max Delay")

        return value
