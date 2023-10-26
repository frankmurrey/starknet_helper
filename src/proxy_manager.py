import aiohttp.typedefs
from typing import Union, Optional
from aiohttp_socks import SocksConnector

from loguru import logger
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.http_client import HttpMethod
from src.schemas.proxy_data import ProxyData
from src.custom_client_session import CustomSession


class ProxyManager:
    def __init__(self, proxy_data: ProxyData):
        self.proxy_data = proxy_data
        self.connector = None

    def get_session(self) -> Union[aiohttp.ClientSession, None]:
        if self.proxy_data:
            return self.get_custom_session_for_proxy()
        else:
            return self.get_custom_session()

    def get_proxy(self) -> Union[dict, None, bool]:
        proxy_data = self.proxy_data
        if proxy_data is None:
            return None

        p_type = proxy_data.proxy_type

        if proxy_data.auth is False:
            return {
                f"{p_type}://": f"{p_type}://{proxy_data.host}:{proxy_data.port}",
            }

        if proxy_data.auth is True:
            return {
                f"{p_type}://": f"{p_type}://{proxy_data.username}:{proxy_data.password}@{proxy_data.host}:{proxy_data.port}",
            }

    async def get_ip(self) -> Union[str, None]:
        try:
            session = self.get_session()
            client = FullNodeClient(node_url="")
            response = await client._client._make_request(
                session=session,
                address="https://api.ipify.org?format=json",
                http_method=HttpMethod.GET,
                payload=None,
                params=None
            )
            await session.close()
            await self.close_connector()

            return response['ip']

        except Exception as ex:
            logger.error(f"Failed to get ip")
            return None

    def get_custom_session_for_proxy(self) -> aiohttp.ClientSession:
        proxies = self.get_proxy()

        proxy_unit: Optional[aiohttp.typedefs.StrOrURL] = (
            proxies.get(f"{self.proxy_data.proxy_type}://") if proxies else None
        )

        if self.proxy_data.proxy_type == 'http':
            self.connector = aiohttp.TCPConnector(limit=10)
            custom_session = CustomSession(proxy=proxy_unit, connector=self.connector)

        elif self.proxy_data.proxy_type == 'socks5':
            self.connector = SocksConnector.from_url(
                url=proxy_unit
            )
            custom_session = CustomSession(connector=self.connector)

        else:
            raise ValueError(f"Unknown proxy type: {self.proxy_data.proxy_type}")

        return custom_session

    def get_custom_session(self) -> aiohttp.ClientSession:
        self.connector = aiohttp.TCPConnector(limit=10)
        custom_session = CustomSession(connector=self.connector)

        return custom_session

    async def close_connector(self):
        if self.connector:
            await self.connector.close()
            self.connector = None
