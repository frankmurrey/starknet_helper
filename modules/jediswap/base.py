import random
from typing import Union
from typing import TYPE_CHECKING

from loguru import logger

from contracts.base import TokenBase
from modules.base import SwapModuleBase
from contracts.jediswap.main import JediSwapContracts

if TYPE_CHECKING:
    from src.schemas.tasks.jediswap import JediSwapTask


class JediSwapBase(SwapModuleBase):
    task: 'JediSwapTask'

    def __init__(self,
                 account,
                 task):

        super().__init__(
            account=account,
            task=task,
        )
        self.jedi_contracts = JediSwapContracts()

        self.router_contract = self.get_contract(address=self.jedi_contracts.router_address,
                                                 abi=self.jedi_contracts.router_abi,
                                                 provider=account)

        self.factory_contract = self.get_contract(address=self.jedi_contracts.factory_address,
                                                  abi=self.jedi_contracts.factory_abi,
                                                  provider=account)

        self._account = account

    async def get_amount_in(self,
                            amount_out_wei: int,
                            coin_x_obj: TokenBase,
                            coin_y_obj: TokenBase,
                            router_contract) -> Union[int, None]:
        """
        Get the amount in for coin pair, using router contract.
        :param amount_out_wei:
        :param coin_x_obj:
        :param coin_y_obj:
        :param router_contract:
        :return:
        """
        path = [int(coin_x_obj.contract_address, 16),
                int(coin_y_obj.contract_address, 16)]

        try:
            amounts_out = await router_contract.functions["get_amounts_out"].call(
                amount_out_wei,
                path
            )
            return amounts_out.amounts[1]

        except Exception as e:
            logger.error(f'Error while getting amount in: {e}')
            return None
