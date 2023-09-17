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
    coin_to_swap: Union[str]
    coin_to_receive: Union[str]

    use_all_balance: Union[bool] = False
    send_percent_balance: Union[bool] = False

    compare_with_cg_price: Union[bool] = True

    min_amount_out: Union[float]
    max_amount_out: Union[float]

    max_price_difference_percent: Union[float] = 2

    slippage: Union[float] = 0.5

    @property
    def action_info(self):
        return f"{self.coin_to_swap.upper()} -> {self.coin_to_receive.upper()}"

    @validator("coin_to_receive", pre=True)
    def validate_coin_to_receive_pre(cls, value, values):

        if value == values["coin_to_swap"]:
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
