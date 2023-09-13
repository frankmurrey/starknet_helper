import random
from typing import Union
from typing import TYPE_CHECKING

from loguru import logger

from contracts.myswap.main import MySwapContracts
from modules.myswap.base import MySwapBase
from modules.myswap.math import calc_output_burn_liquidity

if TYPE_CHECKING:
    from src.schemas.tasks.myswap import MySwapAddLiquidityTask
    from src.schemas.tasks.myswap import MySwapRemoveLiquidityTask


class MySwapAddLiquidity(MySwapBase):

    task: 'MySwapAddLiquidityTask'

    def __init__(self,
                 account,
                 task: 'MySwapAddLiquidityTask', ):
        super().__init__(
            account=account,
            task=task
        )

        self.task = task
        self.account = account

        self.my_swap_contracts = MySwapContracts()
        self.router_contract = self.get_contract(address=self.my_swap_contracts.router_address,
                                                 abi=self.my_swap_contracts.router_abi,
                                                 provider=account)

        self.coin_x = self.tokens.get_by_name(self.task.coin_x)
        self.coin_y = self.tokens.get_by_name(self.task.coin_y)

    async def get_amount_out_x_from_balance(self):
        wallet_token_balance_wei = await self.get_token_balance(token_address=self.coin_x.contract_address,
                                                                account=self.account)

        if wallet_token_balance_wei == 0:
            logger.error(f"Wallet {self.coin_x.symbol.upper()} balance = 0")
            return None

        token_x_decimals = await self.get_token_decimals(contract_address=self.coin_x.contract_address,
                                                         abi=self.coin_x.abi,
                                                         provider=self.account)

        wallet_token_balance_decimals = wallet_token_balance_wei / 10 ** token_x_decimals

        if self.task.use_all_balance_x is True:
            amount_out_wei = wallet_token_balance_wei

        elif self.task.send_percent_balance_x is True:
            percent = random.randint(int(self.task.min_amount_out_x), int(self.task.max_amount_out_x)) / 100
            amount_out_wei = int(wallet_token_balance_wei * percent)

        elif wallet_token_balance_decimals < self.task.max_amount_out_x:
            amount_out_wei = self.get_random_amount_out_of_token(min_amount=self.task.min_amount_out_x,
                                                                 max_amount=wallet_token_balance_decimals,
                                                                 decimals=token_x_decimals)

        else:
            amount_out_wei = self.get_random_amount_out_of_token(
                min_amount=self.task.min_amount_out_x,
                max_amount=self.task.max_amount_out_x,
                decimals=token_x_decimals
            )

        return int(amount_out_wei)

    async def get_amounts_out(self) -> Union[dict, None]:
        amount_out_x_wei = await self.get_amount_out_x_from_balance()
        if amount_out_x_wei is None:
            return None

        reserves_data = await self.get_pool_reserves_data(
            coin_x_symbol=self.task.coin_x,
            coin_y_symbol=self.task.coin_y,
            router_contract=self.router_contract
        )
        if reserves_data is None:
            return None

        amount_out_y_wei = await self.get_amount_in(
            reserves_data=reserves_data,
            amount_out_wei=amount_out_x_wei,
            coin_x_obj=self.coin_x,
            coin_y_obj=self.coin_y,
            slippage=0)

        if amount_out_y_wei is None:
            return None

        return {
            self.coin_x.contract_address: amount_out_x_wei,
            self.coin_y.contract_address: amount_out_y_wei
        }

    async def build_txn_payload_data(self) -> Union[dict, None]:
        amounts_out = await self.get_amounts_out()
        if amounts_out is None:
            return None

        pool_id = self.get_pool_id(
            coin_x_symbol=self.task.coin_x,
            coin_y_symbol=self.task.coin_y
        )
        if pool_id is None:
            return None

        token_pair: list[str, str] = await self.get_token_pair_for_pool(pool_id=pool_id)
        if token_pair is None:
            return None

        token_0_decimals = await self.get_tokens_decimals_by_call(token_address=self.i16(token_pair[0]),
                                                                  account=self.account)
        amount_out_0_wei = int(amounts_out[token_pair[0]])
        amount_out_0_wei_with_slippage = int(amount_out_0_wei * (1 - self.task.slippage / 100))
        amount_0_decimals = amount_out_0_wei / 10 ** token_0_decimals

        token_1_decimals = await self.get_tokens_decimals_by_call(token_address=self.i16(token_pair[1]),
                                                                  account=self.account)
        amount_out_1_wei = int(amounts_out[token_pair[1]])
        amount_out_1_wei_with_slippage = int(amount_out_1_wei * (1 - self.task.slippage / 100))
        amount_1_decimals = amount_out_1_wei / 10 ** token_1_decimals

        approve_call_0 = self.build_token_approve_call(token_addr=token_pair[0],
                                                       spender=hex(self.router_contract.address),
                                                       amount_wei=amount_out_0_wei)
        approve_call_1 = self.build_token_approve_call(token_addr=token_pair[1],
                                                       spender=hex(self.router_contract.address),
                                                       amount_wei=amount_out_1_wei)

        add_liq_call = self.build_call(
            to_addr=self.router_contract.address,
            func_name='add_liquidity',
            call_data=[
                self.i16(token_pair[0]),
                amount_out_0_wei,
                0,
                amount_out_0_wei_with_slippage,
                0,
                self.i16(token_pair[1]),
                amount_out_1_wei,
                0,
                amount_out_1_wei_with_slippage,
                0
            ]
        )

        calls = [approve_call_0, approve_call_1, add_liq_call]

        return {"calls": calls,
                token_pair[0]: amount_0_decimals,
                token_pair[1]: amount_1_decimals
                }

    async def send_txn(self):
        txn_payload_data: dict = await self.build_txn_payload_data()
        if txn_payload_data is None:
            return False

        txn_calls = txn_payload_data['calls']
        amount_out_x_decimals = txn_payload_data[self.coin_x.contract_address]
        amount_out_y_decimals = txn_payload_data[self.coin_y.contract_address]

        txn_info_message = (f"Add Liquidity (MySwap) | "
                            f"{round(amount_out_x_decimals, 5)} ({self.coin_x.symbol.upper()}) "
                            f"+ {round(amount_out_y_decimals, 5)} ({self.coin_y.symbol.upper()}). "
                            f"Slippage: {self.task.slippage}%.")

        txn_status = await self.simulate_and_send_transfer_type_transaction(account=self.account,
                                                                            calls=txn_calls,
                                                                            txn_info_message=txn_info_message, )

        return txn_status


class MySwapRemoveLiquidity(MySwapBase):

    task: 'MySwapRemoveLiquidityTask'

    def __init__(self,
                 account,
                 task: 'MySwapRemoveLiquidityTask', ):
        super().__init__(
            account=account,
            task=task,
        )

        self.account = account
        self.task = task

        self.my_swap_contracts = MySwapContracts()
        self.router_contract = self.get_contract(address=self.my_swap_contracts.router_address,
                                                 abi=self.my_swap_contracts.router_abi,
                                                 provider=account)

        self.coin_x = self.tokens.get_by_name(self.task.coin_x)
        self.coin_y = self.tokens.get_by_name(self.task.coin_y)

    def get_lp_token_address_for_pool(self,
                                      token_0_symbol,
                                      token_1_symbol) -> Union[str, None]:
        lp_symbol = f"msw_{token_0_symbol.lower()}_{token_1_symbol.lower()}"
        lp_token_address = self.tokens.get_by_name(lp_symbol).contract_address

        return lp_token_address

    async def get_lp_supply(self,
                            lp_addr) -> int:
        call = self.build_call(
            to_addr=lp_addr,
            func_name='totalSupply',
            call_data=[]
        )
        resp = await self.account.client.call_contract(call)
        return resp[0]

    async def get_amounts_out(
            self,
            token0_address: str,
            token1_address: str,
            lp_token_address: str,
            lp_amount_out_wei: int) -> Union[dict, None]:

        reserves_data = await self.get_pool_reserves_data(
            coin_x_symbol=self.task.coin_x,
            coin_y_symbol=self.task.coin_y,
            router_contract=self.router_contract
        )
        if reserves_data is None:
            return None

        lp_supply = await self.get_lp_supply(lp_addr=lp_token_address)

        output: tuple = calc_output_burn_liquidity(
            lp_supply=lp_supply,
            to_burn=lp_amount_out_wei,
            reserve_x=reserves_data[self.i16(token0_address)],
            reserve_y=reserves_data[self.i16(token1_address)]
        )

        return {
            token0_address: output[0],
            token1_address: output[1]
        }

    async def build_txn_payload_data(self) -> Union[dict, None]:

        pool_id = self.get_pool_id(
            coin_x_symbol=self.task.coin_x,
            coin_y_symbol=self.task.coin_y
        )
        if pool_id is None:
            return None

        lp_token_address = self.get_lp_token_address_for_pool(
            token_0_symbol=self.pools[pool_id][0],
            token_1_symbol=self.pools[pool_id][1]
        )
        if lp_token_address is None:
            return None

        wallet_lp_balance_wei = await self.get_token_balance_for_address(
            token_address=self.i16(lp_token_address),
            account=self.account,
            address=self.account.address
        )

        if wallet_lp_balance_wei == 0:
            logger.error(f"Wallet {self.coin_x.symbol.upper()} balance = 0")
            return None

        token_pair: list[str, str] = await self.get_token_pair_for_pool(pool_id=pool_id)
        if token_pair is None:
            return None

        amounts_out: dict = await self.get_amounts_out(
            token0_address=token_pair[0],
            token1_address=token_pair[1],
            lp_token_address=lp_token_address,
            lp_amount_out_wei=wallet_lp_balance_wei
        )
        if amounts_out is None:
            return None

        amount_out_0_with_slippage = int(amounts_out[token_pair[0]] * (1 - self.task.slippage / 100))
        amount_out_1_with_slippage = int(amounts_out[token_pair[1]] * (1 - self.task.slippage / 100))

        approve_call = self.build_token_approve_call(token_addr=lp_token_address,
                                                     spender=hex(self.router_contract.address),
                                                     amount_wei=wallet_lp_balance_wei)

        remove_liq_call = self.build_call(
            to_addr=self.router_contract.address,
            func_name='withdraw_liquidity',
            call_data=[
                pool_id,
                wallet_lp_balance_wei,
                0,
                amount_out_0_with_slippage,
                0,
                amount_out_1_with_slippage,
                0
            ]
        )

        token_0_decimals = await self.get_tokens_decimals_by_call(token_address=self.i16(token_pair[0]),
                                                                  account=self.account)
        amount_out_x_decimals = amounts_out[self.coin_x.contract_address] / 10 ** token_0_decimals

        token_1_decimals = await self.get_tokens_decimals_by_call(token_address=self.i16(token_pair[1]),
                                                                  account=self.account)
        amount_out_1_decimals = amounts_out[self.coin_y.contract_address] / 10 ** token_1_decimals

        lp_decimals = await self.get_tokens_decimals_by_call(token_address=self.i16(lp_token_address),
                                                             account=self.account)

        amount_out_lp_decimals = wallet_lp_balance_wei / 10 ** lp_decimals

        calls = [approve_call, remove_liq_call]

        return {"calls": calls,
                "amount_out_lp_decimals": amount_out_lp_decimals,
                token_pair[0]: amount_out_x_decimals,
                token_pair[1]: amount_out_1_decimals
                }

    async def send_txn(self):
        txn_payload: dict = await self.build_txn_payload_data()
        if txn_payload is None:
            return False

        txn_calls = txn_payload['calls']
        amount_out_x_decimals = txn_payload[self.coin_x.contract_address]
        amount_out_y_decimals = txn_payload[self.coin_y.contract_address]
        lp_amount_out_decimals = txn_payload['amount_out_lp_decimals']

        txn_info_message = (f"Remove Liquidity (MySwap). "
                            f"{round(amount_out_x_decimals, 5)} ({self.coin_x.symbol.upper()}) + "
                            f"{round(amount_out_y_decimals, 5)} ({self.coin_y.symbol.upper()}). "
                            f"LP amount out: {lp_amount_out_decimals}. "
                            f"Slippage: {self.task.slippage}%.")

        txn_status = await self.simulate_and_send_transfer_type_transaction(account=self.account,
                                                                            calls=txn_calls,
                                                                            txn_info_message=txn_info_message, )

        return txn_status
