from typing import Union
from typing import TYPE_CHECKING

from loguru import logger
from starknet_py.net.client_errors import ClientError

from modules.base import SwapModuleBase
from contracts.base import TokenBase
from contracts.tokens.main import Tokens
from contracts.sithswap.main import SithSwapContracts
from modules.sithswap.math import get_amount_in_from_reserves

if TYPE_CHECKING:
    from src.schemas.tasks.sithswap import SithSwapTask


class SithBase(SwapModuleBase):
    stable_coin_symbols: list = ['USDC', 'USDT', 'DAI']

    task: 'SithSwapTask'

    def __init__(
            self,
            account,
            task
    ):

        super().__init__(
            account=account,
            task=task,
        )

        self._account = account
        self.tokens = Tokens()
        self.sith_swap_contracts = SithSwapContracts()

        self.router_contract = self.get_contract(
            address=self.sith_swap_contracts.router_address,
            abi=self.sith_swap_contracts.router_abi,
            provider=account
        )

        self.tokens = Tokens()

    def is_pool_stable(
            self,
            coin_x_symbol: str,
            coin_y_symbol: str
    ) -> bool:
        """
        Check if pool is stable
        :param coin_x_symbol:
        :param coin_y_symbol:
        :return:
        """
        return (coin_x_symbol.upper() in self.stable_coin_symbols
                and
                coin_y_symbol.upper() in self.stable_coin_symbols)

    async def get_pool_for_pair(
            self,
            stable: int,
            router_contract,
            coin_x_address: str,
            coin_y_address: str
    ) -> Union[int, None]:
        """
        Get pool id for pair from router
        :param stable:
        :param router_contract:
        :param coin_x_address:
        :param coin_y_address:
        :return:
        """
        try:
            response = await router_contract.functions['pairFor'].call(
                self.i16(coin_x_address),
                self.i16(coin_y_address),
                stable
            )
            return response.res

        except ClientError:
            logger.error(f"Can't get pool for pair {coin_x_address} {coin_y_address}")
            return None

    async def get_sorted_tokens(
            self,
            pool_addr: str,
            pool_abi) -> Union[list[int, int], None]:
        """
        Get sorted tokens for pool
        :param pool_addr:
        :param pool_abi:
        :return:
        """
        try:
            pool_contract = self.get_contract(address=pool_addr,
                                              abi=pool_abi,
                                              provider=self._account)
            response = await pool_contract.functions['getTokens'].call()

            return [response.token0,
                    response.token1]

        except ClientError:
            logger.error(f"Can't get sorted tokens for pool {pool_addr}")
            return None

    async def get_reserves(
            self,
            router_contract,
            coin_x_address: str,
            coin_y_address: str,
            stable: int
    ) -> Union[dict, None]:
        """
        Get reserves for pair
        :param router_contract:
        :param coin_x_address:
        :param coin_y_address:
        :param stable:
        :return:
        """
        try:
            response = await router_contract.functions['getReserves'].call(
                self.i16(coin_x_address),
                self.i16(coin_y_address),
                stable
            )

            return {
                coin_x_address: response.reserve_a,
                coin_y_address: response.reserve_b
            }

        except ClientError:
            logger.error(f"Can't get reserves for {coin_x_address} {coin_y_address}")
            return None

    async def get_direct_amount_in_and_pool_type(
            self,
            amount_in_wei: int,
            coin_x: TokenBase,
            coin_y: TokenBase,
            router_contract
    ) -> Union[dict, None]:
        """
        Get amount in wei and pool type from router function
        :param amount_in_wei:
        :param coin_x:
        :param coin_y:
        :param router_contract:
        :return:
        """
        try:
            response = await router_contract.functions['getAmountOut'].call(
                amount_in_wei,
                self.i16(coin_x.contract_address),
                self.i16(coin_y.contract_address),
            )

            return {
                'amount_in_wei': response.amount,
                'stable': response.stable
            }

        except ClientError:
            logger.error(f"Can't get amount in for {coin_x.symbol.upper()} {coin_y.symbol.upper()}")
            return None

    async def get_amount_in_and_pool_type(
            self,
            amount_in_wei: int,
            coin_x: TokenBase,
            coin_y: TokenBase,
            router_contract
    ) -> Union[dict, None]:
        """
        Calculate amount in wei and pool type from reserves using formula
        :param amount_in_wei:
        :param coin_x:
        :param coin_y:
        :param router_contract:
        :return:
        """

        try:
            is_stable: bool = self.is_pool_stable(
                coin_x_symbol=coin_x.symbol,
                coin_y_symbol=coin_y.symbol
            )
            stable: int = 1 if is_stable is True else 0
            reserves = await self.get_reserves(
                router_contract=router_contract,
                coin_x_address=coin_x.contract_address,
                coin_y_address=coin_y.contract_address,
                stable=stable
            )

            if reserves is None:
                return None

            amount_y_wei = get_amount_in_from_reserves(
                amount_out=amount_in_wei,
                reserve_x=reserves[coin_x.contract_address],
                reserve_y=reserves[coin_y.contract_address]
            )

            return {
                'amount_in_wei': amount_y_wei,
                'stable': stable
            }

        except Exception as e:
            logger.error(f"Error while getting amount in and pool id: {e}")
            return None
