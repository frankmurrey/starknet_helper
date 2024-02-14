from typing import Union
from typing import TYPE_CHECKING

from loguru import logger
from starknet_py.net.client_errors import ClientError

from modules.base import ModuleBase
from contracts.base import TokenBase
from contracts.tokens.main import Tokens
from contracts.starkex.main import StarkExContracts

if TYPE_CHECKING:
    from src.schemas.tasks.starkex import StarkExSwapTask
    from src.schemas.tasks.starkex import AddLiquidityTaskBase
    from src.schemas.tasks.starkex import RemoveLiquidityTaskBase
    from src.schemas.wallet_data import WalletData


class StarkExBase(ModuleBase):
    def __init__(
            self,
            account,
            task: Union[
                'StarkExSwapTask',
                'AddLiquidityTaskBase',
                'RemoveLiquidityTaskBase'
            ],
            wallet_data: 'WalletData',
    ):
        super().__init__(
            account=account,
            task=task,
            wallet_data=wallet_data,
        )

        self.task = task

        self.tokens = Tokens()
        self.starkex_contracts = StarkExContracts()

        self.router_contract = self.get_contract(
            address=self.starkex_contracts.router_address,
            abi=self.starkex_contracts.router_abi,
            provider=account
        )

    async def get_amount_in(
            self,
            amount_out_wei: int,
            coin_x_obj: TokenBase,
            coin_y_obj: TokenBase,
            router_contract
    ) -> Union[int, None]:
        """
        Get the amount in for coin pair, using router contract.
        :param amount_out_wei:
        :param coin_x_obj:
        :param coin_y_obj:
        :param router_contract:
        :return:
        """
        path = [
            int(coin_x_obj.contract_address, 16),
            int(coin_y_obj.contract_address, 16)
        ]

        try:
            amounts_out = await router_contract.functions["getAmountsOut"].call(
                amount_out_wei,
                path
            )
            return amounts_out.amounts[1]

        except Exception as e:
            self.log_error(f'Error while getting amount in: {e}')
            return None
