from typing import Union, Optional
from typing import Callable, Optional
from uuid import UUID, uuid4
from src import enums


from pydantic import BaseModel
from pydantic import Field
from pydantic import validator
from loguru import logger

from src import enums
from src import exceptions
from src.schemas.proxy_data import ProxyData
from utils.key_manager.key_manager import get_argent_addr_from_private_key
from utils.key_manager.key_manager import get_braavos_addr_from_private_key
from utils.proxy import parse_proxy_data
import config


class WalletData(BaseModel):
    name: Optional[str] = None
    private_key: str
    pair_address: Optional[str] = None
    proxy: Optional[ProxyData] = None
    type: enums.PrivateKeyType = enums.PrivateKeyType.argent
    cairo_version: int = 1
    wallet_id: UUID = Field(default_factory=uuid4)
    wallet_status: enums.WalletStatus = enums.WalletStatus.inactive

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
            raise exceptions.AppValidationError(f"Private key is required")

        if len(v) != config.STARK_KEY_LENGTH:
            print(v)
            raise exceptions.AppValidationError("Private key must be 66 characters long")

        return v

    @property
    def address(self) -> str:
        if self.type == enums.PrivateKeyType.argent:
            return hex(get_argent_addr_from_private_key(private_key=self.private_key,
                                                        cairo_version=self.cairo_version))
        elif self.type == enums.PrivateKeyType.braavos:
            return hex(get_braavos_addr_from_private_key(private_key=self.private_key,
                                                         cairo_version=self.cairo_version))
        else:
            raise exceptions.AppValidationError(f"Bad private key type: {self.type}")
