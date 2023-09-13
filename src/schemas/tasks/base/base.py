from typing import Union, Callable

from pydantic import BaseModel
from pydantic import validator

from utlis import validation
from src import enums


class TaskBase(BaseModel):
    module_type: enums.ModuleType
    module_name: enums.ModuleName
    module: Callable

    max_fee: Union[int]
    forced_gas_limit: Union[bool] = False

    # GLOBALS
    wait_for_receipt: Union[bool] = False
    txn_wait_timeout_sec: Union[float] = 60

    min_delay_sec: Union[float] = 40
    max_delay_sec: Union[float] = 80

    test_mode: Union[bool] = True

    @validator("max_fee", pre=True)
    def validate_max_fee_pre(cls, value):

        value = validation.get_converted_to_int(value, "Max Fee")
        value = validation.get_positive(value, "Max Fee", include_zero=False)

        return value

    @validator("txn_wait_timeout_sec", pre=True)
    def validate_txn_wait_timeout_sec_pre(cls, value, values):

        if values["wait_for_receipt"]:
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
