from typing import Union, Optional

from pydantic import BaseModel
from pydantic import validator
from loguru import logger

from src import enums
from src import exceptions
from src.schemas.proxy_data import ProxyData
from utlis.key_manager.key_manager import get_argent_addr_from_private_key
from utlis.key_manager.key_manager import get_braavos_addr_from_private_key
from utlis.proxy import parse_proxy_data


class WalletData(BaseModel):
    name: Optional[str] = None
    private_key: str
    proxy: Optional[ProxyData] = None
    evm_pair_address: Optional[str] = None
    type: enums.PrivateKeyType = enums.PrivateKeyType.argent

    @validator("proxy", pre=True)
    @classmethod
    def validate_proxy(cls, v):
        if isinstance(v, str):
            return parse_proxy_data(proxy_str=v)
        return v

    @validator("type", pre=True)
    @classmethod
    def validate_type(cls, v):
        if isinstance(v, str):
            try:
                return enums.PrivateKeyType[v.lower()]
            except KeyError:
                logger.error("Bad private key type")

        return v

    @property
    def address(self) -> str:
        if self.type == enums.PrivateKeyType.argent:
            return hex(get_argent_addr_from_private_key(private_key=self.private_key))
        elif self.type == enums.PrivateKeyType.braavos:
            return hex(get_braavos_addr_from_private_key(private_key=self.private_key))
        else:
            raise exceptions.AppValidationError(f"Bad private key type: {self.type}")

    @validator("private_key", pre=True)
    def validate_private_key(cls, v):
        if not v:
            raise exceptions.AppValidationError("Private key is required")

        return v
