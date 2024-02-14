from typing import Union, Tuple
from typing import TYPE_CHECKING

from contracts.base import TokenBase
from modules.base import ModuleBase
from modules.myswap.math import get_amount_in_from_reserves
from contracts.myswap.main import MySwapContracts

if TYPE_CHECKING:
    from src.schemas.tasks.myswap import MySwapTask
    from src.schemas.wallet_data import WalletData


class MySwapBase(ModuleBase):
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

    task: 'MySwapTask'

    def __init__(
            self,
            account,
            task,
            wallet_data: 'WalletData',
    ):

        super().__init__(
            account=account,
            task=task,
            wallet_data=wallet_data,
        )

        self.my_swap_contracts = MySwapContracts()
        self.router_contract = self.get_contract(
            address=self.my_swap_contracts.router_address,
            abi=self.my_swap_contracts.router_abi,
            provider=account
        )

    def get_pool_id(
            self,
            coin_x_symbol: str,
            coin_y_symbol: str
    ) -> Union[int, None]:
        """
        Get pool id from pool name
        :param coin_x_symbol:
        :param coin_y_symbol:
        :return:
        """
        coin_x = coin_x_symbol.upper()
        coin_y = coin_y_symbol.upper()

        for pool_id, pool in self.pools.items():
            if coin_x in pool and coin_y in pool:
                return pool_id

        return None

    async def get_token_pair_for_pool(self, pool_id: int) -> Union[list[str, str], None]:
        """
        Get token pair for pool
        :param pool_id:
        :return:
        """
        if pool_id not in self.pools.keys():
            self.log_error(f"Pool id {pool_id} not found in pools")
            return None

        coin_x_symbol = self.pools[pool_id][0]
        coin_y_symbol = self.pools[pool_id][1]

        coin_x_obj = self.tokens.get_by_name(coin_x_symbol)
        coin_y_obj = self.tokens.get_by_name(coin_y_symbol)

        if coin_x_obj is None or coin_y_obj is None:
            self.log_error(f"Failed to get token objects for {coin_x_symbol} and {coin_y_symbol}")
            return None

        return [coin_x_obj.contract_address,
                coin_y_obj.contract_address]

    async def get_pool_reserves_data(
            self,
            coin_x_symbol: str,
            coin_y_symbol: str,
            router_contract
    ) -> Union[dict, None]:
        """
        Get pool reserves data from router
        :param coin_x_symbol:
        :param coin_y_symbol:
        :param router_contract:
        :return:
        """
        pool_id = self.get_pool_id(
            coin_x_symbol=coin_x_symbol,
            coin_y_symbol=coin_y_symbol
        )
        if pool_id is None:
            self.log_error(f"Failed to get pool id for {coin_x_symbol} and {coin_y_symbol}")
            return None

        reserves_data = await router_contract.functions['get_pool'].call(pool_id)
        if reserves_data is None:
            self.log_error(f"Failed to get reserves data for pool id {pool_id}")
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
            reserves_data
    ) -> Union[dict, None]:
        """
        Get sorted reserves
        :param coin_x_address:
        :param coin_y_address:
        :param reserves_data:
        :return:
        """

        token_x_reserve = reserves_data.get(self.i16(coin_x_address))
        token_y_reserve = reserves_data.get(self.i16(coin_y_address))

        if token_x_reserve is None or token_y_reserve is None:
            self.log_error(f"Failed to get reserves for {coin_x_address} and {coin_y_address}")
            return None

        return {
            coin_x_address: token_x_reserve,
            coin_y_address: token_y_reserve,
            "fee": reserves_data['fee'],
            "pool_id": reserves_data['pool_id']
        }

    async def get_amount_in_and_dao_fee(
            self,
            reserves_data: dict,
            amount_out_wei,
            coin_x_obj: TokenBase,
            coin_y_obj: TokenBase
    ) -> Union[Tuple[int, float], None]:
        """
        Get amount in wei from reserves data
        :param reserves_data:
        :param amount_out_wei: amount out from balance
        :param coin_x_obj:
        :param coin_y_obj:
        :param slippage:
        :return:
        """

        sorted_reserves = await self.get_sorted_reserves(
            coin_x_address=coin_x_obj.contract_address,
            coin_y_address=coin_y_obj.contract_address,
            reserves_data=reserves_data
        )
        if sorted_reserves is None:
            self.log_error(
                f"Failed to get sorted reserves for {coin_x_obj.symbol.upper()} and {coin_y_obj.symbol.upper()}"
            )
            return None

        amount_in_wei = get_amount_in_from_reserves(
            amount_out=amount_out_wei,
            reserve_x=sorted_reserves[coin_x_obj.contract_address],
            reserve_y=sorted_reserves[coin_y_obj.contract_address]
        )
        fee = sorted_reserves['fee']

        return amount_in_wei, float(fee)
