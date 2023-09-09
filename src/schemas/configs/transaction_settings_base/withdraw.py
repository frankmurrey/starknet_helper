from typing import Union

from src.schemas.configs.transaction_settings_base.base import TransactionSettingsBase


class WithdrawSettingsBase(TransactionSettingsBase):
    coin_to_withdraw: Union[str]
