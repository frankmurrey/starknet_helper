from typing import Union, List

from loguru import logger

from src.schemas.proxy_data import ProxyData


def parse_proxy_data(proxy_data: str) -> Union[List[ProxyData], None]:
    if not proxy_data:
        return None

    if proxy_data == "##":
        return None

    try:
        if proxy_data.startswith('m$'):
            is_mobile = True
            proxy_data = proxy_data[2:]
        else:
            is_mobile = False

        proxy_data = proxy_data.split(":")
        if len(proxy_data) == 2:
            host, port = proxy_data
            proxy_data = ProxyData(host=host,
                                   port=port,
                                   is_mobile=is_mobile)

        elif len(proxy_data) == 4:
            host, port, username, password = proxy_data
            proxy_data = ProxyData(host=host,
                                   port=port,
                                   username=username,
                                   password=password,
                                   auth=True,
                                   is_mobile=is_mobile)

        else:
            proxy_data = None

        return proxy_data

    except Exception as e:
        logger.error(f"Error while parsing proxy data: {e}")
        logger.exception(e)
        return None
