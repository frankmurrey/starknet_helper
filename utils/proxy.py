from typing import Optional

from loguru import logger

from src.schemas.proxy_data import ProxyData


def parse_proxy_data(proxy_str: str) -> Optional[ProxyData]:
    if not proxy_str:
        return None

    is_mobile = proxy_str.startswith('m$')
    proxy_str = proxy_str[2:] if is_mobile else proxy_str

    try:
        if '://' in proxy_str:
            proxy_type, proxy_str = proxy_str.split('://', 1)
        else:
            proxy_type = 'http'

        if '@' in proxy_str:
            credentials, proxy_str = proxy_str.split('@', 1)

            username, password = credentials.split(':', 1)
            host, port = proxy_str.split(':', 1)
            auth = True
        else:

            auth = proxy_str.count(":") == 3

            if auth:
                host, port, username, password = proxy_str.split(':', 3)
            else:
                host, port = proxy_str.split(':', 1)
                username = password = None

        port = int(port)
        return ProxyData(
            host=host,
            port=port,
            username=username,
            password=password,
            auth=auth,
            is_mobile=is_mobile,
            proxy_type=proxy_type,
        )

    except Exception as e:
        logger.debug(f"Error parsing proxy data: {e}")

    return None
