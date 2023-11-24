import time
from typing import Union

import httpx
import aiohttp
from aiohttp.client import ClientSession
from starknet_py.net.gateway_client import GatewayClient
import numpy as np
from loguru import logger

from utils.repr.gas_price import gas_price_wait_loop
import config


def get_eth_mainnet_gas_price(rpc_url: str):
    try:
        client = httpx.Client()
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_gasPrice",
            "params": [],
            "id": "1"
        }

        resp = client.post(url=rpc_url, json=payload)

        if resp.status_code != 200:
            return None

        gas_price = int(resp.json()['result'], 16) / 1e9
        return round(gas_price, 2)

    except Exception as e:
        return None


async def get_eth_mainnet_gas_price_async(rpc_url: str):
    async with aiohttp.ClientSession() as session:
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_gasPrice",
            "params": [],
            "id": "1"
        }
        async with session.post(url=rpc_url, json=payload) as response:
            return await response.json()


def get_time(
        gas_price: Union[tuple, list, int, float],
        sigmoid_params: list = config.GAS_TIME_EXP_PARAMS,
):
    a, b, c, d = sigmoid_params
    return a / (1 + np.exp(-(c * np.abs(gas_price) + d))) + b


class GasPrice:
    def __init__(
            self,
            block_number: Union[int, str] = 'pending',
            session: ClientSession = None
    ):
        self.block_number = block_number
        self.session = session

    async def get_stark_block_gas_price(self) -> Union[int, None]:
        try:
            client = GatewayClient(
                net="mainnet",
                session=self.session
            )

            block = await client.get_block(self.block_number)
            return block.gas_price

        except Exception as e:
            logger.error(f"Error while getting {self.block_number} block gas price: {e}")
            return None

    async def check_loop(
            self,
            target_price_gwei: int,
    ) -> tuple:
        """
        Checks the current gas price on Starkent pending block and waits until it is lower than the target price.
        :param target_price_gwei:
        :return:
        """

        current_gas_price = await self.get_stark_block_gas_price()
        if current_gas_price is None:
            logger.warning(f"Waiting 1 min for rate limit to reset and trying again to get gas price.")
            time.sleep(60)

            current_gas_price = await self.get_stark_block_gas_price()
            if current_gas_price is None:
                return False, current_gas_price

        current_gas_price_gwei = current_gas_price / 1e9
        if current_gas_price_gwei <= target_price_gwei:
            return True, current_gas_price

        delay = config.DEFAULT_DELAY_SEC

        while True:
            current_gas_price = await self.get_stark_block_gas_price()
            if current_gas_price is None:
                continue

            current_gas_price_gwei = current_gas_price / 1e9
            if current_gas_price_gwei <= target_price_gwei:
                gas_price_wait_loop(
                    target_price_wei=target_price_gwei,
                    current_gas_price=current_gas_price_gwei,
                    time_out_sec=int(delay),
                    end='\n'
                )
                return True, current_gas_price

            delay = (
                    get_time(current_gas_price_gwei, config.GAS_TIME_EXP_PARAMS) -
                    get_time(target_price_gwei, config.GAS_TIME_EXP_PARAMS)
            )
            gas_price_wait_loop(
                target_price_wei=target_price_gwei,
                current_gas_price=current_gas_price_gwei,
                time_out_sec=int(delay),
                end=''
            )

