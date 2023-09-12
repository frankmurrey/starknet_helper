from typing import Union, Optional

from pydantic import BaseModel
from pydantic import validator
from loguru import logger

from src import enums
from src.schemas.proxy_data import ProxyData
from utlis.proxy import parse_proxy_data
from src import exceptions


class WalletData(BaseModel):
    name: Optional[str] = None
    private_key: str
    proxy: Optional[ProxyData] = None
    evm_pair_address: Optional[str] = None
    type: enums.PrivateKeyType = enums.PrivateKeyType.argent

    @validator("proxy", pre=True)
    def validate_proxy(cls, v):
        if isinstance(v, str):
            return parse_proxy_data(proxy_str=v)
        return v

    @validator("type", pre=True)
    def validate_type(cls, v):
        if isinstance(v, str):
            try:
                return enums.PrivateKeyType[v.lower()]
            except KeyError:
                logger.error("Bad private key type")

        return v

    @validator("private_key", pre=True)
    def validate_private_key(cls, v):
        if not v:
            raise exceptions.AppValidationError("Private key is required")

        return v
