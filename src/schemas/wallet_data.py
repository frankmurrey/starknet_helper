from typing import Union

from pydantic import BaseModel

from src.schemas.proxy_data import ProxyData


class WalletData(BaseModel):
    private_key: str
    proxy: Union[ProxyData, None] = None
    evm_pair_address: Union[str, None] = None
