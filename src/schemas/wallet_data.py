from typing import Union

from src import enums
from src.schemas.proxy_data import ProxyData

from pydantic import BaseModel


class WalletData(BaseModel):
    private_key: str
    proxy: Union[ProxyData, None] = None
    evm_pair_address: Union[str, None] = None
    type: str = enums.PrivateKeyType.argent
