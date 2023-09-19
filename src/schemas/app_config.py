from typing import Union

from pydantic import BaseModel
from pydantic import validator
from src import exceptions
from utlis import validation


class AppConfigSchema(BaseModel):
    preserve_logs: bool = True
    rpc_url: str = "https://starknet-mainnet.public.blastapi.io"
    eth_mainnet_rpc_url: str = "https://rpc.ankr.com/eth"
    target_eth_mainnet_gas_price: Union[int, float] = 20
    time_to_wait_target_gas_price_sec: Union[int, float] = 360
    shuffle_wallets: bool = False
    last_wallet_version: str = "0.3.0"

    @validator('rpc_url', pre=True)
    def rpc_url_must_be_valid(cls, value):
        if not value:
            raise exceptions.AppValidationError("RPC URL can't be empty")

        return value

    @validator('eth_mainnet_rpc_url', pre=True)
    def eth_mainnet_rpc_url_must_be_valid(cls, value):
        if not value:
            raise exceptions.AppValidationError("ETH Mainnet RPC URL can't be empty")

        return value

    @validator('target_eth_mainnet_gas_price', pre=True)
    def target_eth_mainnet_gas_price_must_be_valid(cls, value):
        value = validation.get_converted_to_int(value, "Gas Price")
        value = validation.get_positive(value, "Gas Price", include_zero=False)

        return value

    @validator('time_to_wait_target_gas_price_sec', pre=True)
    def time_to_wait_target_gas_price_sec_must_be_valid(cls, value):
        value = validation.get_converted_to_int(value, "Time to wait")
        value = validation.get_positive(value, "Time to wait", include_zero=True)

        return value






