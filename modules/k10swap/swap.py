import time
import random
from typing import Union

from contracts.tokens.main import Tokens
from contracts.k10swap.main import K10SwapContracts

from modules.base import StarkBase

from src.schemas.configs.k10swap import K10SwapConfigSchema

from starknet_py.net.account.account import Account

from loguru import logger


class K10Swap(StarkBase):
    config: K10SwapConfigSchema
    account: Account

    def __init__(self,
                 account,
                 config):
        super().__init__(client=account.client)

        self.config = config
        self.account = account

        self.tokens = Tokens()
        self.k10_swap_contracts = K10SwapContracts()
        self.router_contract = self.get_contract(address=self.k10_swap_contracts.router_address,
                                                 abi=self.k10_swap_contracts.router_abi,
                                                 provider=account)

        self.coin_x = self.tokens.get_by_name(self.config.coin_to_swap)
        self.coin_y = self.tokens.get_by_name(self.config.coin_to_receive)

    async def get_amount_out_from_balance(self):
        wallet_token_balance_wei = await self.get_token_balance(token_address=self.coin_x.contract_address,
                                                                account=self.account)

        if wallet_token_balance_wei == 0:
            logger.error(f"Wallet {self.coin_x.symbol.upper()} balance = 0")
            return None

        token_decimals = await self.get_token_decimals(contract_address=self.coin_x.contract_address,
                                                       abi=self.coin_x.abi,
                                                       provider=self.account)

        wallet_token_balance_decimals = wallet_token_balance_wei / 10 ** token_decimals

        if self.config.use_all_balance is True:
            amount_out_wei = wallet_token_balance_wei

        elif self.config.send_percent_balance is True:
            percent = random.randint(self.config.min_amount_out, self.config.max_amount_out) / 100
            amount_out_wei = int(wallet_token_balance_wei * percent)

        elif wallet_token_balance_decimals < self.config.max_amount_out:
            amount_out_wei = self.get_random_amount_out_of_token(min_amount=self.config.min_amount_out,
                                                                 max_amount=wallet_token_balance_decimals,
                                                                 decimals=token_decimals)

        else:
            amount_out_wei = self.get_random_amount_out_of_token(
                min_amount=self.config.min_amount_out,
                max_amount=self.config.max_amount_out,
                decimals=token_decimals
            )

        return amount_out_wei

    async def get_amount_in(self,
                            amount_in_wei):
        path = [int(self.coin_x.contract_address, 16),
                int(self.coin_y.contract_address, 16)]

        try:
            amounts_out = await self.router_contract.functions["getAmountsOut"].call(
                amount_in_wei,
                path
            )

            return amounts_out

        except Exception as e:
            logger.error(f'Error while getting amount in: {e}')
            return None

    async def build_txn_payload_data(self) -> Union[dict, None]:
        amount_x_wei = await self.get_amount_out_from_balance()
        coin_x_decimals = await self.get_token_decimals(contract_address=self.coin_x.contract_address,
                                                        abi=self.coin_x.abi,
                                                        provider=self.account)
        amount_x_decimals = amount_x_wei / 10 ** coin_x_decimals

        if amount_x_wei is None:
            return None

        amounts_in_wei = await self.get_amount_in(amount_x_wei)
        if amounts_in_wei is None:
            return None

        amount_y_wei = amounts_in_wei.amounts[1]
        amount_in_wei_with_slippage = int(amount_y_wei * (1 - (self.config.slippage / 100)))
        coin_y_decimals = await self.get_token_decimals(contract_address=self.coin_y.contract_address,
                                                        abi=self.coin_y.abi,
                                                        provider=self.account)
        amount_y_decimals = amount_y_wei / 10 ** coin_y_decimals

        approve_call = self.build_token_approve_call(token_addr=self.coin_x.contract_address,
                                                     spender=hex(self.router_contract.address),
                                                     amount_wei=int(amount_x_wei))

        swap_deadline = int(time.time() + 1000)
        swap_call = self.build_call(to_addr=self.router_contract.address,
                                    func_name='swapExactTokensForTokens',
                                    call_data=[amount_x_wei,
                                               0,
                                               amount_in_wei_with_slippage,
                                               0,
                                               2,
                                               self.i16(self.coin_x.contract_address),
                                               self.i16(self.coin_y.contract_address),
                                               self.account.address,
                                               swap_deadline])
        calls = [approve_call, swap_call]

        return {
            'calls': calls,
            'amount_x_decimals': amount_x_decimals,
            'amount_y_decimals': amount_y_decimals,
        }

    async def send_swap_txn(self):
        txn_payload_data = await self.build_txn_payload_data()
        if txn_payload_data is None:
            return False

        txn_status = await self.send_swap_type_txn(
            account=self.account,
            config=self.config,
            txn_payload_data=txn_payload_data
        )

        return txn_status