from typing import Union

from contracts.base import TokenBase
from contracts.tokens.main import Tokens
from modules.base import SwapModuleBase
from modules.myswap.math import get_amount_in_from_reserves
from src.schemas.tasks.myswap import MySwapTask

from loguru import logger


class MySwapBase(SwapModuleBase):
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

    task: MySwapTask

    def __init__(
            self,
            account,
            task: MySwapTask, ):

        super().__init__(
            client=account.client,
            task=task,
        )
        self._account = account

        self.tokens = Tokens()

    def get_pool_id(self,
                    coin_x_symbol: str,
                    coin_y_symbol: str) -> Union[int, None]:
        coin_x = coin_x_symbol.upper()
        coin_y = coin_y_symbol.upper()

        for pool_id, pool in self.pools.items():
            if coin_x in pool and coin_y in pool:
                return pool_id

        return None

    async def get_token_pair_for_pool(self,
                                      pool_id: int) -> Union[list, None]:
        if pool_id not in self.pools.keys():
            return None

        coin_x_symbol = self.pools[pool_id][0]
        coin_y_symbol = self.pools[pool_id][1]

        coin_x_obj = self.tokens.get_by_name(coin_x_symbol)
        coin_y_obj = self.tokens.get_by_name(coin_y_symbol)

        if coin_x_obj is None or coin_y_obj is None:
            return None

        return [coin_x_obj.contract_address, coin_y_obj.contract_address]

    async def get_pool_reserves_data(
            self,
            coin_x_symbol: str,
            coin_y_symbol: str,
            router_contract) -> Union[dict, None]:
        pool_id = self.get_pool_id(
            coin_x_symbol=coin_x_symbol,
            coin_y_symbol=coin_y_symbol
        )
        if pool_id is None:
            return None

        reserves_data = await router_contract.functions['get_pool'].call(pool_id)
        if reserves_data is None:
            return None

        token_a_address = reserves_data.pool['token_a_address']
        token_a_reserves = reserves_data.pool['token_a_reserves']

        token_b_address = reserves_data.pool['token_b_address']
        token_b_reserves = reserves_data.pool['token_b_reserves']

        fee = reserves_data.pool['fee_percentage']

        reserves = {
            token_a_address: token_a_reserves,
            token_b_address: token_b_reserves,
            "fee": fee,
            "pool_id": pool_id
        }

        return reserves

    async def get_sorted_reserves(
            self,
            coin_x_address: str,
            coin_y_address: str,
            reserves_data):

        token_x_reserve = reserves_data.get(self.i16(coin_x_address))
        token_y_reserve = reserves_data.get(self.i16(coin_y_address))

        if token_x_reserve is None or token_y_reserve is None:
            return None

        return {
            coin_x_address: token_x_reserve,
            coin_y_address: token_y_reserve,
            "fee": reserves_data['fee'],
            "pool_id": reserves_data['pool_id']
        }

    async def get_amount_in(
            self,
            reserves_data: dict,
            amount_out_wei,
            coin_x_obj: TokenBase,
            coin_y_obj: TokenBase,
            slippage: int
    ):

        sorted_reserves = await self.get_sorted_reserves(coin_x_address=coin_x_obj.contract_address,
                                                         coin_y_address=coin_y_obj.contract_address,
                                                         reserves_data=reserves_data)
        if sorted_reserves is None:
            return None

        amount_in_wei = get_amount_in_from_reserves(amount_out=amount_out_wei,
                                                    reserve_x=sorted_reserves[coin_x_obj.contract_address],
                                                    reserve_y=sorted_reserves[coin_y_obj.contract_address])
        fee = sorted_reserves['fee']

        amount_in_after_slippage = amount_in_wei * (1 - (slippage / 100))
        amount_in_after_dao_fee = amount_in_after_slippage * (1 - (fee / 100000))

        return int(amount_in_after_dao_fee)
