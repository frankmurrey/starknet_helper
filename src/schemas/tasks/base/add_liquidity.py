from typing import Union

from pydantic import validator

from src.schemas import validation_mixins
from src.schemas.tasks.base import TaskBase
from src.exceptions import AppValidationError
from utlis import validation
from src import enums


class AddLiquidityTaskBase(
    TaskBase,
    validation_mixins.SlippageValidationMixin,
    validation_mixins.SameCoinValidationMixin
):
    coin_x: Union[str]
    coin_y: Union[str]

    use_all_balance_x: Union[bool] = False
    send_percent_balance_x: Union[bool] = False

    min_amount_out_x: Union[float] = 0
    max_amount_out_x: Union[float] = 0

    slippage: Union[float] = 0.5

    @validator("min_amount_out_x", pre=True)
    def validate_min_amount_out_x_pre(cls, value, values):

        if values["use_all_balance_x"]:
            value = 0

        value = validation.get_converted_to_float(value, "Min Amount Out X")
        value = validation.get_positive(value, "Min Amount Out X", include_zero=False)

        return value

    @validator("max_amount_out_x", pre=True)
    def validate_max_amount_out_x_pre(cls, value, values):

        if "min_amount_out_x" not in values:
            raise AppValidationError("Min Amount Out X is required")

        if values["use_all_balance_x"]:
            value = 0

        value = validation.get_converted_to_float(value, "Max Amount Out X")
        value = validation.get_positive(value, "Max Amount Out X", include_zero=False)
        value = validation.get_greater(value, values["min_amount_out_x"], "Max Amount Out X")

        return value
