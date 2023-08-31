import time
import random

from contracts.tokens.main import Tokens
from contracts.myswap.main import MySwapContracts

from modules.base import StarkBase
from modules.myswap.math import get_amount_in_from_reserves

from src.schemas.configs.myswap import MySwapConfigSchema

from starknet_py.net.account.account import Account

from loguru import logger


class MySwap(StarkBase):
    config: MySwapConfigSchema
    account: Account
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

    def __init__(self,
                 account,
                 config):
        super().__init__(client=account.client)

        self.config = config
        self.account = account

        self.tokens = Tokens()
        self.my_swap_contracts = MySwapContracts()
        self.router_contract = self.get_contract(address=self.my_swap_contracts.router_address,
                                                 abi=self.my_swap_contracts.router_abi,
                                                 provider=account)

        self.coin_x = self.tokens.get_by_name(self.config.coin_to_swap)
        self.coin_y = self.tokens.get_by_name(self.config.coin_to_receive)

        self.amount_out_decimals = None
        self.amount_in_decimals = None

        self.pool_id = None

    def get_pool_id(self):
        coin_x = self.coin_x.symbol.upper()
        coin_y = self.coin_y.symbol.upper()

        for pool_id, pool in self.pools.items():
            if coin_x in pool and coin_y in pool:
                return pool_id

        return None

    async def get_pool_reserves(self):
        pool_id = self.get_pool_id()
        if pool_id is None:
            return None

        self.pool_id = pool_id
        reserves_data = await self.router_contract.functions['get_pool'].call(pool_id)
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
            "fee": fee
        }

        return reserves

    async def get_sorted_reserves(self):
        reserves_data = await self.get_pool_reserves()
        if reserves_data is None:
            return None

        token_x_reserve = reserves_data.get(self.i16(self.coin_x.contract_address))
        token_y_reserve = reserves_data.get(self.i16(self.coin_y.contract_address))

        if token_x_reserve is None or token_y_reserve is None:
            return None

        return {
            self.coin_x.contract_address: token_x_reserve,
            self.coin_y.contract_address: token_y_reserve,
            "fee": reserves_data['fee']
        }

    async def get_amount_in(self,
                            amount_out_wei):
        sorted_reserves = await self.get_sorted_reserves()
        if sorted_reserves is None:
            return None

        amount_in_wei = get_amount_in_from_reserves(amount_out=amount_out_wei,
                                                    reserve_x=sorted_reserves[self.coin_x.contract_address],
                                                    reserve_y=sorted_reserves[self.coin_y.contract_address])
        fee = sorted_reserves['fee']

        amount_in_after_slippage = amount_in_wei * (1 - (self.config.slippage / 100))
        amount_in_after_dao_fee = amount_in_after_slippage * (1 - (fee / 100000))

        token_y_decimals = await self.get_token_decimals(contract_address=self.coin_y.contract_address,
                                                         abi=self.coin_y.abi,
                                                         provider=self.account)
        self.amount_in_decimals = amount_in_after_dao_fee / 10 ** token_y_decimals

        return int(amount_in_after_dao_fee)

    async def get_amount_out_from_balance(self):
        wallet_token_balance_wei = await self.get_token_balance(token_address=self.coin_x.contract_address,
                                                                account=self.account)

        if wallet_token_balance_wei == 0:
            logger.error(f"Wallet {self.coin_x.symbol.upper()} balance = 0")
            return None

        token_x_decimals = await self.get_token_decimals(contract_address=self.coin_x.contract_address,
                                                         abi=self.coin_x.abi,
                                                         provider=self.account)

        wallet_token_balance_decimals = wallet_token_balance_wei / 10 ** token_x_decimals

        if self.config.use_all_balance is True:
            amount_out_wei = wallet_token_balance_wei

        elif self.config.send_percent_balance is True:
            percent = random.randint(self.config.min_amount_out, self.config.max_amount_out) / 100
            amount_out_wei = int(wallet_token_balance_wei * percent)

        elif wallet_token_balance_decimals < self.config.max_amount_out:
            amount_out_wei = self.get_random_amount_out_of_token(min_amount=self.config.min_amount_out,
                                                                 max_amount=wallet_token_balance_decimals,
                                                                 decimals=token_x_decimals)

        else:
            amount_out_wei = self.get_random_amount_out_of_token(
                min_amount=self.config.min_amount_out,
                max_amount=self.config.max_amount_out,
                decimals=token_x_decimals
            )

        self.amount_out_decimals = amount_out_wei / 10 ** token_x_decimals

        return int(amount_out_wei)

    async def build_txn_payload_calls(self):
        amount_out_wei = await self.get_amount_out_from_balance()
        if amount_out_wei is None:
            return None

        amount_in_wei = await self.get_amount_in(amount_out_wei=amount_out_wei)
        if amount_in_wei is None:
            return None

        approve_call = self.build_token_approve_call(token_addr=self.coin_x.contract_address,
                                                     spender=hex(self.router_contract.address),
                                                     amount_wei=int(amount_out_wei))
        swap_call = self.build_call(to_addr=self.router_contract.address,
                                    func_name='swap',
                                    call_data=[self.pool_id,
                                               self.i16(self.coin_x.contract_address),
                                               amount_out_wei,
                                               0,
                                               amount_in_wei,
                                               0])
        calls = [approve_call, swap_call]

        return calls

    async def send_swap_txn(self):
        txn_payload_calls = await self.build_txn_payload_calls()
        if txn_payload_calls is None:
            return False

        txn_info_message = (f"Swap (MySwap) | {round(self.amount_out_decimals, 4)} ({self.coin_x.symbol.upper()}) -> "
                            f"{round(self.amount_in_decimals, 4)} ({self.coin_y.symbol.upper()}). "
                            f"Slippage: {self.config.slippage}%.")

        txn_status = await self.simulate_and_send_transfer_type_transaction(account=self.account,
                                                                            calls=txn_payload_calls,
                                                                            txn_info_message=txn_info_message,
                                                                            config=self.config)

        return txn_status
