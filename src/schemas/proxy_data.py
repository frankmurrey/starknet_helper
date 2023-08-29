from typing import Union

from pydantic import BaseModel


class ProxyData(BaseModel):
    host: str
    port: Union[int, str]
    username: str = None
    password: str = None
    auth: bool = False
    is_mobile: bool = False
