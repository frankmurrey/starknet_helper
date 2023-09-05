from typing import Union

from loguru import logger
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.http_client import HttpMethod


class GeckoPricer:
    def __init__(self, client: FullNodeClient):
        self.client = client

    async def get_simple_price_of_token_pair(self,
                                             x_token_id: str,
                                             y_token_id: str) -> Union[dict, None]:
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                "ids": f"{x_token_id},{y_token_id}",
                "vs_currencies": "usd"
            }

            response = await self.client._client.request(
                address=url,
                http_method=HttpMethod.GET,
                params=params,
                payload=None,
            )

            x_token_price = response.get(x_token_id).get("usd")
            y_token_price = response.get(y_token_id).get("usd")

            if x_token_price is None or y_token_price is None:
                return None

            return {x_token_id: x_token_price,
                    y_token_id: y_token_price}

        except Exception as e:
            logger.error(e)
            return None

    async def is_target_price_valid(
            self,
            x_token_id: str,
            y_token_id: str,
            x_amount: Union[int, float],
            y_amount: Union[int, float],
            max_price_difference_percent: Union[int, float]) -> tuple[bool, Union[dict]]:

        try:
            gecko_coins_data: dict = await self.get_simple_price_of_token_pair(
                x_token_id=x_token_id,
                y_token_id=y_token_id
            )
            if gecko_coins_data is None:
                logger.error(f"Error while getting price data from CoinGecko")
                return False, {'gecko_price': None,
                               'target_price': None}

            target_price = round(y_amount / x_amount, 4)
            gecko_price = gecko_coins_data[x_token_id] / gecko_coins_data[y_token_id]

            price_data = {'gecko_price': gecko_price,
                          'target_price': target_price}

            if gecko_price < target_price:
                return True, price_data

            if gecko_price > target_price:
                price_difference = gecko_price - target_price
                price_difference_percent = (price_difference / target_price) * 100
                if price_difference_percent <= max_price_difference_percent:
                    return True, price_data
                else:
                    return False, price_data

            return False, price_data

        except Exception as e:
            logger.error(f"Error while validating target price: {e}")
            return False, {'gecko_price': None,
                           'target_price': None}
