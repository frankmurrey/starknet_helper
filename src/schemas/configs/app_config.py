from typing import Union

from pydantic import BaseModel

from src.enums import PrivateKeyType


class AppConfigSchema(BaseModel):
    preserve_logs: bool = True
    mobile_proxy_rotation: bool = False
    mobile_proxy_rotation_link: Union[str, None] = ""
    rpc_url: str = "https://starknet-mainnet.public.blastapi.io"

    shuffle_wallets: bool = False
    private_key_type: PrivateKeyType = PrivateKeyType.argent
