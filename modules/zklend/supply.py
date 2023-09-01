import random

from modules.base import StarkBase
from contracts.tokens.main import Tokens
from contracts.zklend.main import ZkLendContracts
from src.schemas.configs.zklend import ZkLendSupplyConfigSchema

from loguru import logger


class ZkLendSupply(StarkBase):
    config: ZkLendSupplyConfigSchema

    def __init__(
            self,
            account,
            config):
        super().__init__(client=account.client)

        self.config = config
        self.account = account

        self.tokens = Tokens()
        self.zk_lend_contracts = ZkLendContracts()
        self.router_contract = self.get_contract(address=self.zk_lend_contracts.router_address,
                                                 abi=self.zk_lend_contracts.router_abi,
                                                 provider=account)

        self.coin_x = self.tokens.get_by_name(self.config.coin_to_supply)

        self.amount_out_decimals = None

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

    async def build_deposit_call(self,
                                 amount_out_wei: int):
        deposit_call = self.build_call(to_addr=self.router_contract.address,
                                       func_name='deposit',
                                       call_data=[
                                           self.i16(self.coin_x.contract_address),
                                           amount_out_wei
                                       ])

        return deposit_call

    def build_enable_collateral_call(self):
        enable_collateral_call = self.build_call(to_addr=self.router_contract.address,
                                                 func_name='enable_collateral',
                                                 call_data=[
                                                     self.i16(self.coin_x.contract_address)
                                                 ])

        return enable_collateral_call

    async def build_txn_payload_calls(self):
        amount_out_wei = await self.get_amount_out_from_balance()
        if amount_out_wei is None:
            return None

        approve_call = self.build_token_approve_call(token_addr=self.coin_x.contract_address,
                                                     spender=hex(self.router_contract.address),
                                                     amount_wei=int(amount_out_wei))

        deposit_call = await self.build_deposit_call(amount_out_wei=amount_out_wei)

        calls = [approve_call, deposit_call]

        if self.config.enable_collateral is True:
            enable_collateral_call = self.build_enable_collateral_call()
            calls.append(enable_collateral_call)

        return calls

    async def send_supply_txn(self):
        txn_payload_calls = await self.build_txn_payload_calls()
        if txn_payload_calls is None:
            return False

        txn_info_message = (f"Supply (ZkLend) | {round(self.amount_out_decimals, 4)} ({self.coin_x.symbol.upper()}). "
                            f"Enable collateral: {self.config.enable_collateral}.")

        txn_status = await self.simulate_and_send_transfer_type_transaction(account=self.account,
                                                                            calls=txn_payload_calls,
                                                                            txn_info_message=txn_info_message,
                                                                            config=self.config)

        return txn_status
