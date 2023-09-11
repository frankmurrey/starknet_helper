from typing import Union

from src.schemas import validation_mixins
from src.schemas.tasks.base import TaskBase


class SupplyTaskBase(
    TaskBase,
    validation_mixins.MinMaxAmountOutValidationMixin,
):
    coin_to_supply: Union[str]

    use_all_balance: Union[bool] = False
    send_percent_balance: Union[bool] = False
    enable_collateral: Union[bool] = False

    min_amount_out: Union[float]
    max_amount_out: Union[float]
