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
    coin_x: str
    coin_y: str

    use_all_balance: bool = False
    send_percent_balance: bool = False

    min_amount_out: float = 0
    max_amount_out: float = 0

    slippage: float = 2

    @property
    def action_info(self):
        return f"{self.coin_x.upper()} + {self.coin_y.upper()}"

    @validator("min_amount_out", pre=True)
    def validate_min_amount_out_pre(cls, value, values):

        if values["use_all_balance"]:
            return 0

        value = validation.get_converted_to_float(value, "Min Amount Out")
        value = validation.get_positive(value, "Min Amount Out", include_zero=False)

        return value

    @validator("max_amount_out", pre=True)
    def validate_max_amount_out_pre(cls, value, values):

        if values["use_all_balance"]:
            return 0

        if "min_amount_out" not in values:
            raise AppValidationError("Min Amount Out is required")

        value = validation.get_converted_to_float(value, "Max Amount Out")
        value = validation.get_positive(value, "Max Amount Out", include_zero=False)
        value = validation.get_greater(value, values["min_amount_out"], "Max Amount Out")

        return value
