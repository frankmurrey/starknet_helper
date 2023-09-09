from typing import Union

from src.schemas.configs import validation_mixins
from src.schemas.configs.transaction_settings_base.base import TransactionSettingsBase


class RemoveLiquiditySettingsBase(
    TransactionSettingsBase,
    validation_mixins.SlippageValidationMixin,
    validation_mixins.SameCoinValidationMixin
):
    coin_x: Union[str]
    coin_y: Union[str]
    slippage: Union[float] = 0.5
