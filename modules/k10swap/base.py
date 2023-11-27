from typing import Union
from typing import Tuple
from typing import TYPE_CHECKING

from loguru import logger

from contracts.base import TokenBase
from modules.base import ModuleBase
from contracts.k10swap.main import K10SwapContracts
from starknet_py.serialization import TupleDataclass

if TYPE_CHECKING:
    from src.schemas.tasks.k10swap import K10SwapTask
    from src.schemas.tasks.k10swap import K10SwapAddLiquidityTask
    from src.schemas.tasks.k10swap import K10SwapRemoveLiquidityTask
    from src.schemas.wallet_data import WalletData


class K10SwapBase(ModuleBase):
    def __init__(
            self,
            account,
            task: Union[
                'K10SwapTask',
                'K10SwapAddLiquidityTask',
                'K10SwapRemoveLiquidityTask'
            ],
            wallet_data: 'WalletData',
    ):
        super().__init__(
            account=account,
            task=task,
            wallet_data=wallet_data,
        )

        self.k10_contracts = K10SwapContracts()

        self.router_contract = self.get_contract(
            address=self.k10_contracts.router_address,
            abi=self.k10_contracts.router_abi,
            provider=account)

        self.factory_contract = self.get_contract(
            address=self.k10_contracts.factory_address,
            abi=self.k10_contracts.factory_abi,
            provider=account
        )

    async def get_amounts_in(
            self,
            coin_x: TokenBase,
            coin_y: TokenBase,
            amount_in_wei: int,
    ) -> Union[TupleDataclass, None]:
        """
        Get the amount in for coin pair, using router contract.
        :param coin_x:
        :param coin_y:
        :param amount_in_wei:
        :return:
        """
        path = [
            int(coin_x.contract_address, 16),
            int(coin_y.contract_address, 16)
        ]

        try:
            amounts_out = await self.router_contract.functions["getAmountsOut"].call(
                amount_in_wei,
                path
            )

            return amounts_out

        except Exception as e:
            self.log_error(f'Error while getting amount in: {e}')
            return None

    async def get_token_pair_address(
            self,
            coin_x: TokenBase,
            coin_y: TokenBase,
    ) -> Union[int, None]:
        """
        Get the token pair.
        :return:
        """
        try:
            pair = await self.factory_contract.functions["getPair"].call(
                int(coin_x.contract_address, 16),
                int(coin_y.contract_address, 16)
            )
            return pair.pair

        except Exception as e:
            self.log_error(f'Error while getting pool data: {e}')
            return None

    async def get_token_pair(
            self,
            token_pair_address: int
    ) -> Union[Tuple[int, int], None]:
        """
        Get the token pair.
        :return:
        """
        try:
            pool_contract = self.get_contract(
                address=token_pair_address,
                abi=self.k10_contracts.pool_abi,
                provider=self.account
            )

            token0_address = await pool_contract.functions["token0"].call()
            token1_address = await pool_contract.functions["token1"].call()

            return token0_address.token0, token1_address.token1

        except Exception as e:
            self.log_error(f'Error while getting pool data: {e}')
            return None


