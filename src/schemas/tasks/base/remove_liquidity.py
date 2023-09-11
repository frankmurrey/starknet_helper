from typing import Union

from src.schemas import validation_mixins
from src.schemas.tasks.base import TaskBase


class RemoveLiquidityTaskBase(
    TaskBase,
    validation_mixins.SlippageValidationMixin,
    validation_mixins.SameCoinValidationMixin
):
    coin_x: Union[str]
    coin_y: Union[str]
    slippage: Union[float] = 0.5
