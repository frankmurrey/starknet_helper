from typing import Union

from src.schemas.configs import validation_mixins
from src.schemas.configs.transaction_settings_base.base import TransactionSettingsBase


class SupplySettingsBase(
    TransactionSettingsBase,
    validation_mixins.MinMaxAmountOutValidationMixin,
):
    coin_to_supply: Union[str]

    min_amount_out: Union[float]
    max_amount_out: Union[float]

    use_all_balance: Union[bool] = False
    send_percent_balance: Union[bool] = False
    enable_collateral: Union[bool] = False

