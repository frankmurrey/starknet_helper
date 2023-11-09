import asyncio
import time
from typing import Union

import httpx
import aiohttp
from aiohttp.client import ClientSession
from starknet_py.net.gateway_client import GatewayClient
from loguru import logger

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


class GasPrice:
    def __init__(
            self,
            block_number: Union[int, str],
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
            target_price_wei: int,
            time_out_sec: int,
            is_timeout_needed: bool
    ) -> tuple:
        """
        Checks the current gas price on Starkent pending block and waits until it is lower than the target price.
        :param is_timeout_needed:
        :param target_price_wei:
        :param time_out_sec:
        :return:
        """

        current_gas_price = await self.get_stark_block_gas_price()
        if current_gas_price is None:
            logger.warning(f"Waiting 1 min for rate limit to reset and trying again to get gas price.")
            time.sleep(60)

            current_gas_price = await self.get_stark_block_gas_price()
            if current_gas_price is None:
                return False, current_gas_price

        if current_gas_price <= target_price_wei:
            return True, current_gas_price

        msg = f"Waiting for gas price to be lower than {target_price_wei / 10 ** 9} Gwei. " \
              f"(Current - {round(current_gas_price / 10 ** 9, 2)} Gwei) "

        if is_timeout_needed is True:
            msg += f"Timeout: {time_out_sec} sec."

        logger.info(msg)

        start_time = time.time()
        delay = config.DEFAULT_DELAY_SEC
        while True:
            current_gas_price = await self.get_stark_block_gas_price()
            if current_gas_price is None:
                continue

            if current_gas_price <= target_price_wei:
                return True, current_gas_price

            if is_timeout_needed is True:
                delay *= 2
                if time.time() - start_time > time_out_sec:
                    return False, current_gas_price

            time.sleep(delay)


if __name__ == '__main__':
    gas = asyncio.run(get_eth_mainnet_gas_price_async('https://rpc.ankr.com/eth'))
    print(gas)
