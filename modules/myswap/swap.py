import random
from typing import Union

from contracts.tokens.main import Tokens
from contracts.myswap.main import MySwapContracts

from modules.myswap.base import MySwapBase

from src.schemas.configs.myswap import MySwapConfigSchema

from starknet_py.net.account.account import Account

from loguru import logger


class MySwap(MySwapBase):
    config: MySwapConfigSchema
    account: Account

    def __init__(self,
                 account,
                 config):
        super().__init__(account=account)

        self.config = config
        self.account = account

        self.tokens = Tokens()
        self.my_swap_contracts = MySwapContracts()
        self.router_contract = self.get_contract(address=self.my_swap_contracts.router_address,
                                                 abi=self.my_swap_contracts.router_abi,
                                                 provider=account)

        self.coin_x = self.tokens.get_by_name(self.config.coin_to_swap)
        self.coin_y = self.tokens.get_by_name(self.config.coin_to_receive)

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

        return int(amount_out_wei)

    async def build_txn_payload_data(self) -> Union[dict, None]:
        amount_out_wei = await self.get_amount_out_from_balance()
        if amount_out_wei is None:
            return None

        reserves_data = await self.get_pool_reserves_data(coin_x_symbol=self.coin_x.symbol,
                                                          coin_y_symbol=self.coin_y.symbol,
                                                          router_contract=self.router_contract)
        if reserves_data is None:
            return None

        amount_in_wei = await self.get_amount_in(
            reserves_data=reserves_data,
            amount_out_wei=amount_out_wei,
            coin_x_obj=self.coin_x,
            coin_y_obj=self.coin_y,
            slippage=self.config.slippage)

        if amount_in_wei is None:
            return None

        token_x_decimals = await self.get_token_decimals(contract_address=self.coin_x.contract_address,
                                                         abi=self.coin_x.abi,
                                                         provider=self.account)
        amount_x_decimals = amount_out_wei / 10 ** token_x_decimals

        token_y_decimals = await self.get_token_decimals(contract_address=self.coin_y.contract_address,
                                                         abi=self.coin_y.abi,
                                                         provider=self.account)
        amount_y_decimals = amount_in_wei / 10 ** token_y_decimals

        approve_call = self.build_token_approve_call(token_addr=self.coin_x.contract_address,
                                                     spender=hex(self.router_contract.address),
                                                     amount_wei=int(amount_out_wei))
        swap_call = self.build_call(to_addr=self.router_contract.address,
                                    func_name='swap',
                                    call_data=[reserves_data['pool_id'],
                                               self.i16(self.coin_x.contract_address),
                                               amount_out_wei,
                                               0,
                                               amount_in_wei,
                                               0])
        calls = [approve_call, swap_call]

        return {
            "calls": calls,
            "amount_x_decimals": amount_x_decimals,
            "amount_y_decimals": amount_y_decimals
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
