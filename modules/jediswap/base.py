import random
from typing import Union
from typing import TYPE_CHECKING

from loguru import logger

from contracts.base import TokenBase
from modules.base import SwapModuleBase

if TYPE_CHECKING:
    from src.schemas.tasks.jediswap import JediSwapTask


class JediSwapBase(SwapModuleBase):
    task: 'JediSwapTask'

    def __init__(self,
                 account,
                 task):

        super().__init__(
            client=account.client,
            task=task,
        )
        self._account = account

    async def get_amounts_out_from_balance(
            self,
            coin_x_obj: TokenBase,
            use_all_balance: bool,
            send_percent_balance: bool,
            min_amount_out: Union[int, float],
            max_amount_out: Union[int, float],

    ) -> Union[dict, None]:
        wallet_token_balance_wei = await self.get_token_balance(token_address=self.i16(coin_x_obj.contract_address),
                                                                account=self._account)

        if wallet_token_balance_wei == 0:
            logger.error(f"Wallet {coin_x_obj.symbol.upper()} balance = 0")
            return None

        token_decimals = await self.get_token_decimals(contract_address=coin_x_obj.contract_address,
                                                       abi=coin_x_obj.abi,
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

        return {'amount_wei': amount_out_wei,
                'amount_decimals': amount_out_wei / 10 ** token_decimals}

    async def get_amounts_in(self,
                             amount_out_wei: int,
                             coin_x_obj: TokenBase,
                             coin_y_obj: TokenBase,
                             router_contract):
        path = [int(coin_x_obj.contract_address, 16),
                int(coin_y_obj.contract_address, 16)]

        try:
            amounts_out = await router_contract.functions["get_amounts_out"].call(
                amount_out_wei,
                path
            )

            token_decimals = await self.get_token_decimals(contract_address=coin_y_obj.contract_address,
                                                           abi=coin_y_obj.abi,
                                                           provider=self._account)

            return {'amount_wei': amounts_out.amounts[1],
                    'amount_decimals': amounts_out.amounts[1] / 10 ** token_decimals}

        except Exception as e:
            logger.error(f'Error while getting amount in: {e}')
            return None
