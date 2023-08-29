import time
import random

from contracts.tokens.main import Tokens
from contracts.myswap.main import MySwapContracts

from modules.base import StarkBase

from src.schemas.configs.myswap import MySwapConfigSchema

from starknet_py.net.account.account import Account

from loguru import logger


class MySwap(StarkBase):
    config: MySwapConfigSchema
    account: Account
    pools: dict = {
        1: ['ETH', 'USDC'],
        2: ['DAI', 'ETH'],
        3: ['WBTC', 'USDC'],
        4: ['ETH', 'USDT'],
        5: ['USDC', 'USDT'],
        6: ['DAI', 'USDC'],
        7: ['tETH', 'ETH'],
        8: ['ORDS', 'ETH'],
    }

    def __init__(self,
                 account,
                 config):
        super().__init__(client=account.client)

        self.config = config
        self.account = account

        self.tokens = Tokens()
        self.my_swap_contracts = MySwapContracts()
        self.router_contract = self.get_contract(address=self.my_swap_contracts.router_address,
                                                 abi=self.my_swap_contracts.router_abi,
                                                 provider=account)

        self.coin_x = self.tokens.get_by_name(self.config.coin_to_swap)
        self.coin_y = self.tokens.get_by_name(self.config.coin_to_receive)

        self.amount_out_decimals = None
        self.amount_in_decimals = None

    def get_pool_id(self):
        coin_x = self.coin_x.symbol.upper()
        coin_y = self.coin_y.symbol.upper()

        for pool_id, pool in self.pools.items():
            if coin_x in pool and coin_y in pool:
                return pool_id

        return None

    def get_sorted_pair(self):
        pool_id = self.get_pool_id()
        if pool_id is None:
            return None

        pool = self.pools[pool_id]

    async def get_pool_reserves(self):
        pool_id = self.get_pool_id()
        reserves_data = await self.router_contract.functions['get_pool'].call(pool_id)
        print(reserves_data)








