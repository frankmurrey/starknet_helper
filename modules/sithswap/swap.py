import time
import random

from contracts.tokens.main import Tokens
from contracts.sithswap.main import SithSwapContracts

from modules.base import StarkBase

from src.schemas.configs.sithswap import SithSwapConfigSchema

from starknet_py.net.account.account import Account

from loguru import logger


class SithSwap(StarkBase):
    config: SithSwapConfigSchema
    account: Account

    def __init__(self,
                 account,
                 config):
        super().__init__(client=account.client)

        self.config = config
        self.account = account

        self.tokens = Tokens()
        self.sith_swap_contracts = SithSwapContracts()
        self.router_contract = self.get_contract(address=self.sith_swap_contracts.router_address,
                                                 abi=self.sith_swap_contracts.router_abi,
                                                 provider=account)

        self.coin_x = self.tokens.get_by_name(self.config.coin_to_swap)
        self.coin_y = self.tokens.get_by_name(self.config.coin_to_receive)

        self.amount_out_decimals = None
        self.amount_in_decimals = None

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

        self.amount_out_decimals = amount_out_wei / 10 ** token_decimals
        return amount_out_wei

    async def get_amount_in_and_pool_id(self,
                                        amount_in_wei):
        try:
            amounts_out_data = await self.router_contract.functions["getAmountOut"].call(
                amount_in_wei,
                self.i16(self.coin_x.contract_address),
                self.i16(self.coin_y.contract_address)
            )

            decimals = await self.get_token_decimals(contract_address=self.coin_y.contract_address,
                                                     abi=self.coin_x.abi,
                                                     provider=self.account)
            self.amount_in_decimals = (amounts_out_data.amount / 10 ** decimals) * (1 - (self.config.slippage / 100))
            return amounts_out_data
        except Exception as e:
            logger.error(f"Error while getting amount in and pool id: {e}")
            return None

    async def build_txn_payload_calls(self):
        amount_out_wei = await self.get_amount_out_from_balance()

        if amount_out_wei is None:
            return None

        amounts_in_data = await self.get_amount_in_and_pool_id(amount_out_wei)
        if amounts_in_data is None:
            return None

        amount_in = amounts_in_data.amount
        amount_in_wei_with_slippage = int(amount_in * (1 - (self.config.slippage / 100)))
        is_stable = amounts_in_data.stable

        approve_call = self.build_token_approve_call(token_addr=self.coin_x.contract_address,
                                                     spender=hex(self.router_contract.address),
                                                     amount_wei=int(amount_out_wei))

        swap_deadline = int(time.time() + 1000)
        swap_call = self.build_call(to_addr=self.router_contract.address,
                                    func_name='swapExactTokensForTokens',
                                    call_data=[amount_out_wei,
                                               0,
                                               amount_in_wei_with_slippage,
                                               0,
                                               1,
                                               self.i16(self.coin_x.contract_address),
                                               self.i16(self.coin_y.contract_address),
                                               is_stable,
                                               self.account.address,
                                               swap_deadline])
        calls = [approve_call, swap_call]
        return calls

    async def send_swap_txn(self):
        txn_payload_calls = await self.build_txn_payload_calls()
        if txn_payload_calls is None:
            return False

        txn_info_message = (f"Swap (SithSwap) | {round(self.amount_out_decimals, 4)} ({self.coin_x.symbol.upper()}) -> "
                            f"{round(self.amount_in_decimals, 4)} ({self.coin_y.symbol.upper()}). "
                            f"Slippage: {self.config.slippage}%.")

        txn_status = await self.simulate_and_send_transfer_type_transaction(account=self.account,
                                                                            calls=txn_payload_calls,
                                                                            txn_info_message=txn_info_message,
                                                                            config=self.config)

        return txn_status
