from typing import Union

from pydantic import BaseModel

from src.enums import PrivateKeyType


class AppConfigSchema(BaseModel):
    preserve_logs: bool = True
    mobile_proxy_rotation: bool = False
    mobile_proxy_rotation_link: Union[str, None] = ""
    rpc_url: str = "https://starknet-mainnet.public.blastapi.io"
    eth_mainnet_rpc_url: str = "https://rpc.ankr.com/eth"
    target_eth_mainnet_gas_price: Union[int, float] = 20
    time_to_wait_target_gas_price_sec: Union[int, float] = 360

    shuffle_wallets: bool = False
    private_key_type: PrivateKeyType = PrivateKeyType.argent
