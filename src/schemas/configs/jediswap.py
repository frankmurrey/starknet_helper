from typing import Union

from src.schemas.configs.base import CommonSettingsBase


class JediSwapConfigSchema(CommonSettingsBase):
    module_name: str = 'jediswap_swap'
    coin_to_swap: Union[str, None] = ""
    coin_to_receive: Union[str, None] = ""
    min_amount_out: Union[int, float, str] = 0
    max_amount_out: Union[int, float, str] = 0
    use_all_balance: Union[bool, str] = False
    send_percent_balance: Union[bool, str] = False
    slippage: Union[int, float, str] = 0
