from typing import Union

from pydantic import BaseModel


class CommonSettingsBase(BaseModel):
    gas_price: Union[int, str] = 0
    gas_limit: Union[int, str] = 0
    forced_gas_limit: Union[bool, str] = False
    wait_for_receipt: Union[bool, str] = False
    txn_wait_timeout_sec: Union[int, str] = 60
    min_delay_sec: Union[int, str] = 0
    max_delay_sec: Union[int, str] = 0
    test_mode: Union[bool, str] = True
