import random
from typing import Union

from modules.base import ModuleBase
from contracts.base import TokenBase
from contracts.tokens.main import Tokens
from modules.sithswap.math import get_amount_in_from_reserves
from src.schemas.tasks.sithswap import SithSwapTask

from loguru import logger
from starknet_py.net.client_errors import ClientError


class SithBase(ModuleBase):
    stable_coin_symbols: list = ['USDC', 'USDT', 'DAI']

    task: SithSwapTask

    def __init__(self,
                 account,
                 task: SithSwapTask):

        super().__init__(
            client=account.client,
            task=task,
        )

        self._account = account

        self.tokens = Tokens()

    def is_pool_stable(self,
                       coin_x_symbol: str,
                       coin_y_symbol: str) -> bool:
        return coin_x_symbol.upper() in self.stable_coin_symbols and coin_y_symbol.upper() in self.stable_coin_symbols

    async def get_pool_for_pair(
            self,
            stable: int,
            router_contract,
            coin_x_address: str,
            coin_y_address: str) -> Union[int, None]:
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
        try:
            pool_contract = self.get_contract(address=pool_addr,
                                              abi=pool_abi,
                                              provider=self._account)
            response = await pool_contract.functions['getTokens'].call()
            return [response.token0, response.token1]
        except ClientError:
            logger.error(f"Can't get sorted tokens for pool {pool_addr}")
            return None

    async def get_reserves(self,
                           router_contract,
                           coin_x_address: str,
                           coin_y_address: str,
                           stable: int) -> Union[dict, None]:
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

    async def get_amount_out_from_balance(
            self,
            coin_x: TokenBase,
            use_all_balance: bool,
            send_percent_balance: bool,
            min_amount_out: Union[int, float],
            max_amount_out: Union[int, float]) -> Union[int, None]:

        wallet_token_balance_wei = await self.get_token_balance(token_address=self.i16(coin_x.contract_address),
                                                                account=self._account)

        if wallet_token_balance_wei == 0:
            logger.error(f"Wallet {coin_x.symbol.upper()} balance = 0")
            return None

        token_decimals = await self.get_token_decimals(contract_address=coin_x.contract_address,
                                                       abi=coin_x.abi,
                                                       provider=self._account)

        wallet_token_balance_decimals = wallet_token_balance_wei / 10 ** token_decimals

        if use_all_balance is True:
            amount_out_wei = wallet_token_balance_wei

        elif send_percent_balance is True:
            percent = random.randint(min_amount_out, max_amount_out) / 100
            amount_out_wei = int(wallet_token_balance_wei * percent)

        elif wallet_token_balance_decimals < max_amount_out:
            amount_out_wei = self.get_random_amount_out_of_token(min_amount=min_amount_out,
                                                                 max_amount=wallet_token_balance_decimals,
                                                                 decimals=token_decimals)

        else:
            amount_out_wei = self.get_random_amount_out_of_token(
                min_amount=min_amount_out,
                max_amount=max_amount_out,
                decimals=token_decimals
            )

        return amount_out_wei

    async def get_direct_amount_in_and_pool_type(
            self,
            amount_in_wei: int,
            coin_x: TokenBase,
            coin_y: TokenBase,
            router_contract) -> Union[dict, None]:
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
            router_contract) -> Union[dict, None]:

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
