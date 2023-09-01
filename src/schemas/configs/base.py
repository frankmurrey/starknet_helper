from typing import Union

from pydantic import BaseModel

from src import enums


class CommonSettingsBase(BaseModel):
    module_type: enums.ModuleType
    module_name: enums.ModuleName

    gas_price: Union[int, str] = 0
    gas_limit: Union[int, str] = 0
    forced_gas_limit: Union[bool, str] = False
    wait_for_receipt: Union[bool, str] = False
    txn_wait_timeout_sec: Union[int, str] = 60
    min_delay_sec: Union[int, str] = 0
    max_delay_sec: Union[int, str] = 0
    test_mode: Union[bool, str] = True


class SwapSettingsBase(CommonSettingsBase):
    coin_to_swap: Union[str, None] = ""
    coin_to_receive: Union[str, None] = ""
    min_amount_out: Union[int, float, str] = 0
    max_amount_out: Union[int, float, str] = 0
    use_all_balance: Union[bool, str] = False
    send_percent_balance: Union[bool, str] = False
    slippage: Union[int, float, str] = 0


class SupplySettingsBase(CommonSettingsBase):
    coin_to_supply: Union[str, None] = ""
    min_amount_out: Union[int, float, str] = 0
    max_amount_out: Union[int, float, str] = 0
    use_all_balance: Union[bool, str] = False
    send_percent_balance: Union[bool, str] = False
    enable_collateral: Union[bool, str] = False


class WithdrawSettingsBase(CommonSettingsBase):
    coin_to_withdraw: Union[str, None] = ""
