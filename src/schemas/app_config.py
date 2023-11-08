from typing import Union

from pydantic import BaseModel
from pydantic import validator
from src import exceptions
from utils import validation


class AppConfigSchema(BaseModel):
    preserve_logs: bool = True
    use_proxy: bool = True
    rpc_url: str = "https://starknet-mainnet.public.blastapi.io"
    target_gas_price: Union[int, float] = 20
    is_gas_price_wait_timeout_needed: bool = False
    time_to_wait_target_gas_price_sec: Union[int, float] = 360
    wallets_amount_to_execute_in_test_mode: int = 3
    last_wallet_version: str = "0.3.0"

    debug: bool = False

    @validator('rpc_url', pre=True)
    def rpc_url_must_be_valid(cls, value):
        if not value:
            raise exceptions.AppValidationError("RPC URL can't be empty")

        return value

    @validator('target_gas_price', pre=True)
    def target_gas_price_must_be_valid(cls, value):
        value = validation.get_converted_to_int(value, "Gas Price")
        value = validation.get_positive(value, "Gas Price", include_zero=False)

        return value

    @validator('time_to_wait_target_gas_price_sec', pre=True)
    def time_to_wait_target_gas_price_sec_must_be_valid(cls, value, values):
        if values['is_gas_price_wait_timeout_needed'] is False:
            return 0

        value = validation.get_converted_to_int(value, "Time to wait")
        value = validation.get_positive(value, "Time to wait", include_zero=True)

        return value

    @validator('wallets_amount_to_execute_in_test_mode', pre=True)
    def wallets_amount_to_execute_in_test_mode_must_be_valid(cls, value):
        value = validation.get_converted_to_int(value, "Wallets amount")
        value = validation.get_positive(value, "Wallets amount", include_zero=False)

        return value
