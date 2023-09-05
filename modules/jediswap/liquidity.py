import time
from typing import Union

from contracts.tokens.main import Tokens
from contracts.jediswap.main import JediSwapContracts

from modules.jediswap.base import JediSwapBase
from modules.jediswap.math import get_lp_burn_output

from src.schemas.configs.jediswap import JediSwapAddLiquidityConfigSchema
from src.schemas.configs.jediswap import JediSwapRemoveLiquidityConfigSchema


from loguru import logger


class JediSwapAddLiquidity(JediSwapBase):
    config: JediSwapAddLiquidityConfigSchema

    def __init__(self,
                 account,
                 config):
        super().__init__(account=account)

        self.config = config
        self.account = account

        self.tokens = Tokens()
        self.jedi_contracts = JediSwapContracts()
        self.router_contract = self.get_contract(address=self.jedi_contracts.router_address,
                                                 abi=self.jedi_contracts.router_abi,
                                                 provider=account)

        self.coin_x = self.tokens.get_by_name(self.config.coin_x)
        self.coin_y = self.tokens.get_by_name(self.config.coin_y)

        self.amount_x_out_decimals = None
        self.amount_y_out_decimals = None

    async def build_txn_payload_calls(self):
        amounts_x_out: dict = await self.get_amounts_out_from_balance(
            coin_x_obj=self.coin_x,
            use_all_balance=self.config.use_all_balance_x,
            send_percent_balance=self.config.send_percent_balance_x,
            min_amount_out=self.config.min_amount_out_x,
            max_amount_out=self.config.max_amount_out_x
        )
        if amounts_x_out is None:
            return None

        amount_x_out_wei = amounts_x_out['amount_wei']
        amount_x_out_wei_with_slippage = int(amount_x_out_wei * (1 - (self.config.slippage / 100)))
        self.amount_x_out_decimals = amounts_x_out['amount_decimals']

        amounts_y_out: dict = await self.get_amounts_in(amount_out_wei=amount_x_out_wei,
                                                        coin_x_obj=self.coin_x,
                                                        coin_y_obj=self.coin_y,
                                                        router_contract=self.router_contract)
        if amounts_y_out is None:
            return None

        amount_y_out_wei = amounts_y_out['amount_wei']
        amount_y_out_wei_with_slippage = int(amount_y_out_wei * (1 - (self.config.slippage / 100)))
        self.amount_y_out_decimals = amounts_y_out['amount_decimals']

        txn_deadline = int(time.time() + 3600)

        approve_x_call = self.build_token_approve_call(token_addr=self.coin_x.contract_address,
                                                       spender=hex(self.router_contract.address),
                                                       amount_wei=int(amount_x_out_wei))

        approve_y_call = self.build_token_approve_call(token_addr=self.coin_y.contract_address,
                                                       spender=hex(self.router_contract.address),
                                                       amount_wei=int(amount_y_out_wei))

        add_liq_call = self.build_call(to_addr=self.router_contract.address,
                                       func_name='add_liquidity',
                                       call_data=[
                                           self.i16(self.coin_x.contract_address),
                                           self.i16(self.coin_y.contract_address),
                                           int(amount_x_out_wei),
                                           0,
                                           int(amount_y_out_wei),
                                           0,
                                           amount_x_out_wei_with_slippage,
                                           0,
                                           amount_y_out_wei_with_slippage,
                                           0,
                                           self.account.address,
                                           txn_deadline
                                       ])

        calls = [approve_x_call, approve_y_call, add_liq_call]

        return calls

    async def send_add_liq_txn(self):
        txn_payload_calls = await self.build_txn_payload_calls()
        if txn_payload_calls is None:
            return False

        txn_info_message = (f"Add Liquidity (JediSwap) | "
                            f"{round(self.amount_x_out_decimals, 5)} ({self.coin_x.symbol.upper()}) "
                            f"+ {round(self.amount_y_out_decimals, 5)} ({self.coin_y.symbol.upper()}). "
                            f"Slippage: {self.config.slippage}%.")
        txn_status = await self.simulate_and_send_transfer_type_transaction(account=self.account,
                                                                            calls=txn_payload_calls,
                                                                            txn_info_message=txn_info_message,
                                                                            config=self.config)

        return txn_status


class JediSwapRemoveLiquidity(JediSwapBase):
    config: JediSwapRemoveLiquidityConfigSchema

    def __init__(self,
                 account,
                 config):
        super().__init__(account=account)

        self.config = config
        self.account = account

        self.tokens = Tokens()
        self.jedi_contracts = JediSwapContracts()
        self.router_contract = self.get_contract(address=self.jedi_contracts.router_address,
                                                 abi=self.jedi_contracts.router_abi,
                                                 provider=account)

        self.factory_contract = self.get_contract(address=self.jedi_contracts.factory_address,
                                                  abi=self.jedi_contracts.factory_abi,
                                                  provider=account)

        self.coin_x = self.tokens.get_by_name(self.config.coin_x)
        self.coin_y = self.tokens.get_by_name(self.config.coin_y)

        self.amount_out_decimals = None

    async def get_pool_address(self) -> Union[int, None]:
        try:
            response = await self.factory_contract.functions['get_pair'].call(
                self.i16(self.coin_x.contract_address),
                self.i16(self.coin_y.contract_address)
            )

            pool_addr = response.pair

            if pool_addr == 0:
                logger.error(f"Can not find pool address for "
                             f"{self.coin_x.symbol.upper()} and {self.coin_y.symbol.upper()}")
                return None

            return pool_addr
        except Exception as e:
            logger.error(f"Error while getting pool address: {e}")
            return None

    async def get_lp_supply(self,
                            lp_addr) -> int:
        call = self.build_call(
            to_addr=lp_addr,
            func_name='totalSupply',
            call_data=[]
        )
        resp = await self.account.client.call_contract(call)
        return resp[0]

    async def get_token_0_in_pool(self,
                                  pool_addr) -> int:
        call = self.build_call(
            to_addr=pool_addr,
            func_name='token0',
            call_data=[]
        )
        resp = await self.account.client.call_contract(call)
        return resp[0]

    async def get_token_1_in_pool(self,
                                  pool_addr) -> int:
        call = self.build_call(
            to_addr=pool_addr,
            func_name='token1',
            call_data=[]
        )
        resp = await self.account.client.call_contract(call)
        return resp[0]

    async def get_amounts_out(
            self,
            pool_addr,
            lp_amount_out_wei: int) -> Union[tuple, None]:
        token0_addr = await self.get_token_0_in_pool(pool_addr=pool_addr)
        token1_addr = await self.get_token_1_in_pool(pool_addr=pool_addr)

        pool_token0_balance = await self.get_token_balance_for_address(
            token_address=token0_addr,
            account=self.account,
            address=pool_addr
        )
        pool_token1_balance = await self.get_token_balance_for_address(
            token_address=token1_addr,
            account=self.account,
            address=pool_addr
        )

        lp_supply = await self.get_lp_supply(lp_addr=pool_addr)

        output: tuple = get_lp_burn_output(
            amount_to_burn=lp_amount_out_wei,
            total_supply=lp_supply,
            contract_balance_x=pool_token0_balance,
            contract_balance_y=pool_token1_balance
        )
        return output

    async def build_txn_payload_calls(self):
        pool_addr = await self.get_pool_address()
        if pool_addr is None:
            return None

        wallet_lp_balance = await self.get_token_balance(token_address=pool_addr,
                                                         account=self.account)

        if wallet_lp_balance == 0:
            logger.error(f"Wallet LP ({self.coin_x.symbol.upper()} + {self.coin_y.symbol.upper()}) balance = 0")
            return None

        lp_decimals = await self.get_tokens_decimals_by_call(token_address=pool_addr,
                                                             account=self.account)
        self.amount_out_decimals = wallet_lp_balance / 10 ** lp_decimals

        amounts_out: tuple = await self.get_amounts_out(pool_addr=pool_addr,
                                                        lp_amount_out_wei=wallet_lp_balance)
        if amounts_out is None:
            return None

        approve_call = self.build_token_approve_call(token_addr=hex(pool_addr),
                                                     spender=hex(self.router_contract.address),
                                                     amount_wei=int(wallet_lp_balance))

        amount_x_out_wei = amounts_out[0]
        amount_y_out_wei = amounts_out[1]

        amount_x_out_with_slippage = int(amount_x_out_wei * (1 - (self.config.slippage / 100)))
        amount_y_out_with_slippage = int(amount_y_out_wei * (1 - (self.config.slippage / 100)))

        dead_line = int(time.time() + 3600)

        remove_liq_call = self.build_call(to_addr=self.router_contract.address,
                                          func_name='remove_liquidity',
                                          call_data=[
                                              self.i16(self.coin_x.contract_address),
                                              self.i16(self.coin_y.contract_address),
                                              int(wallet_lp_balance),
                                              0,
                                              amount_x_out_with_slippage,
                                              0,
                                              amount_y_out_with_slippage,
                                              0,
                                              self.account.address,
                                              dead_line
                                          ])

        calls = [approve_call, remove_liq_call]

        return calls

    async def send_remove_liq_txn(self):
        txn_payload_calls = await self.build_txn_payload_calls()
        if txn_payload_calls is None:
            return False

        txn_info_message = (f"Remove Liquidity (JediSwap). "
                            f"Pool: {self.coin_x.symbol.upper()} + {self.coin_y.symbol.upper()}. "
                            f"LP amount out: {self.amount_out_decimals}. "
                            f"Slippage: {self.config.slippage}%.")

        txn_status = await self.simulate_and_send_transfer_type_transaction(account=self.account,
                                                                            calls=txn_payload_calls,
                                                                            txn_info_message=txn_info_message,
                                                                            config=self.config)

        return txn_status
