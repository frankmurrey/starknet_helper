from typing import Union

from pydantic import validator

from src.schemas import validation_mixins
from src.schemas.tasks.base import TaskBase
from src.exceptions import AppValidationError
from utlis import validation


class SwapTaskBase(
    TaskBase,
    validation_mixins.SlippageValidationMixin,
    validation_mixins.MinMaxAmountOutValidationMixin,
):
    coin_x: str
    coin_y: str

    use_all_balance: bool = False
    send_percent_balance: bool = False

    compare_with_cg_price: bool = True

    min_amount_out: float
    max_amount_out: float

    max_price_difference_percent: float = 2

    slippage: float = 0.5

    @property
    def action_info(self):
        if self.reverse_action:
            return f"{self.coin_x.upper()} <-> {self.coin_y.upper()}"
        else:
            return f"{self.coin_x.upper()} -> {self.coin_y.upper()}"

    @validator("coin_y", pre=True)
    def validate_coin_to_receive_pre(cls, value, values):

        if value == values["coin_x"]:
            raise AppValidationError("Coin to receive cannot be the same as Coin to swap")

        return value

    @validator("max_price_difference_percent", pre=True)
    def validate_max_price_difference_percent_pre(cls, value, values):

        if not values["compare_with_cg_price"]:
            return 0

        value = validation.get_converted_to_float(value, "Max Price Difference Percent")
        value = validation.get_positive(value, "Max Price Difference Percent", include_zero=True)
        value = validation.get_lower(value, 100, "Max Price Difference Percent", include_max=False)

        return value
