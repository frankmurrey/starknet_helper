import warnings
from typing import Optional

import aiohttp.typedefs
from aiohttp.client import ClientSession


warnings.filterwarnings("ignore", category=DeprecationWarning)


class CustomSession(ClientSession):
    proxy: Optional[aiohttp.typedefs.StrOrURL]

    def __init__(
            self,
            *args,
            proxy: Optional[aiohttp.typedefs.StrOrURL] = None,
            **kwargs
    ):
        super().__init__(
            *args,
            **kwargs
        )
        self.proxy = proxy

    async def _request(
            self,
            *args,
            **kwargs
    ):
        return await super()._request(
            *args,
            **kwargs,
            proxy=self.proxy
        )

