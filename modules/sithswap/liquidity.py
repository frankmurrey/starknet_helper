import time
from typing import TYPE_CHECKING

from loguru import logger
from starknet_py.net.client_errors import ClientError
from starknet_py.net.account.account import Account


from modules.sithswap.base import SithBase
from modules.sithswap.math import calc_output_burn_liquidity
from contracts.tokens.main import Tokens
from contracts.sithswap.main import SithSwapContracts


if TYPE_CHECKING:
    from src.schemas.tasks.sithswap import SithSwapAddLiquidityTask
    from src.schemas.tasks.sithswap import SithSwapRemoveLiquidityTask


class SithSwapAddLiquidity(SithBase):
    task: 'SithSwapAddLiquidityTask'

    def __init__(self,
                 account,
                 task: 'SithSwapAddLiquidityTask'):

        super().__init__(
            account=account,
            task=task
        )

        self.task = task
        self.account: Account = account

        self.tokens = Tokens()
        self.sith_swap_contracts = SithSwapContracts()

        self.router_contract = self.get_contract(address=self.sith_swap_contracts.router_address,
                                                 abi=self.sith_swap_contracts.router_abi,
                                                 provider=account)

        self.coin_x = self.tokens.get_by_name(self.task.coin_x)
        self.coin_y = self.tokens.get_by_name(self.task.coin_y)

    async def get_amounts_out_data(self):
        amount_out_x_wei = await self.get_amount_out_from_balance(
            coin_x=self.coin_x,
            use_all_balance=self.task.use_all_balance_x,
            send_percent_balance=self.task.send_percent_balance_x,
            min_amount_out=self.task.min_amount_out_x,
            max_amount_out=self.task.max_amount_out_x
        )
        if amount_out_x_wei is None:
            logger.error(f"Can't get amount out for {self.coin_x.symbol.upper()}")
            return None

        token_x_decimals = await self.get_token_decimals(
            contract_address=self.coin_x.contract_address,
            abi=self.coin_x.abi,
            provider=self.account
        )
        amount_out_x_decimals = amount_out_x_wei / 10 ** token_x_decimals

        amount_out_y_data: dict = await self.get_amount_in_and_pool_type(
            amount_in_wei=amount_out_x_wei,
            coin_x=self.coin_x,
            coin_y=self.coin_y,
            router_contract=self.router_contract
        )

        if amount_out_y_data is None:
            logger.error(f"Can't get amount in for {self.coin_x.symbol.upper()} {self.coin_y.symbol.upper()}")
            return None

        amount_out_y_wei = amount_out_y_data['amount_in_wei']
        stable = amount_out_y_data['stable']

        token_y_decimals = await self.get_token_decimals(
            contract_address=self.coin_y.contract_address,
            abi=self.coin_y.abi,
            provider=self.account
        )

        amount_out_y_decimals = amount_out_y_wei / 10 ** token_y_decimals

        pool_addr = await self.get_pool_for_pair(
            stable=stable,
            coin_x_address=self.coin_x.contract_address,
            coin_y_address=self.coin_y.contract_address,
            router_contract=self.router_contract
        )
        if pool_addr is None:
            logger.error(f"Can't get pool for {self.coin_x.symbol.upper()} {self.coin_y.symbol.upper()}")
            return None

        return {
            self.i16(self.coin_x.contract_address): amount_out_x_wei,
            self.i16(self.coin_y.contract_address): amount_out_y_wei,
            'amount_x_decimals': amount_out_x_decimals,
            'amount_y_decimals': amount_out_y_decimals,
            'stable': stable,
            'pool_addr': pool_addr
        }

    async def build_txn_payload_data(
            self,
            amounts_out_data: dict
    ):
        sorted_pair: list = await self.get_sorted_tokens(
            pool_addr=amounts_out_data['pool_addr'],
            pool_abi=self.sith_swap_contracts.pool_abi)
        if sorted_pair is None:
            return None

        token0_addr: int = sorted_pair[0]
        token1_addr: int = sorted_pair[1]

        amount_out_0_wei: int = amounts_out_data[token0_addr]
        amount_out_0_wei_with_slippage: int = int(amount_out_0_wei - (amount_out_0_wei * self.task.slippage / 100))

        amount_out_1_wei: int = amounts_out_data[token1_addr]
        amount_out_1_wei_with_slippage: int = int(amount_out_1_wei - (amount_out_1_wei * self.task.slippage / 100))

        approve_call_0 = self.build_token_approve_call(
            token_addr=hex(token0_addr),
            spender=self.sith_swap_contracts.router_address,
            amount_wei=amount_out_0_wei
        )

        approve_call_1 = self.build_token_approve_call(
            token_addr=hex(token1_addr),
            spender=self.sith_swap_contracts.router_address,
            amount_wei=amount_out_1_wei
        )

        deadline: int = int(time.time() + 3600)

        add_liquidity_call = self.build_call(
            to_addr=self.router_contract.address,
            func_name='addLiquidity',
            call_data=[
                token0_addr,
                token1_addr,
                amounts_out_data['stable'],
                amount_out_0_wei,
                0,
                amount_out_1_wei,
                0,
                amount_out_0_wei_with_slippage,
                0,
                amount_out_1_wei_with_slippage,
                0,
                self.account.address,
                deadline
            ]
        )

        calls = [approve_call_0, approve_call_1, add_liquidity_call]

        return calls

    async def send_txn(self):
        amounts_out_data: dict = await self.get_amounts_out_data()
        if amounts_out_data is None:
            return None

        txn_calls = await self.build_txn_payload_data(amounts_out_data=amounts_out_data)
        if txn_calls is None:
            return None

        txn_info_message = (f"Add Liquidity (SithSwap) | "
                            f"{round(amounts_out_data['amount_x_decimals'], 4)} ({self.coin_x.symbol.upper()}) + "
                            f"{round(amounts_out_data['amount_y_decimals'], 4)} ({self.coin_y.symbol.upper()}). "
                            f"Slippage: {self.task.slippage}%.")

        txn_status = await self.simulate_and_send_transfer_type_transaction(account=self.account,
                                                                            calls=txn_calls,
                                                                            txn_info_message=txn_info_message, )

        return txn_status


class SithSwapRemoveLiquidity(SithBase):
    task: 'SithSwapRemoveLiquidityTask'

    def __init__(self,
                 account,
                 task: 'SithSwapRemoveLiquidityTask'):

        super().__init__(
            account=account,
            task=task,
        )

        self.task = task
        self.account: Account = account

        self.tokens = Tokens()
        self.sith_swap_contracts = SithSwapContracts()

        self.router_contract = self.get_contract(address=self.sith_swap_contracts.router_address,
                                                 abi=self.sith_swap_contracts.router_abi,
                                                 provider=account)

        self.coin_x = self.tokens.get_by_name(self.task.coin_x)
        self.coin_y = self.tokens.get_by_name(self.task.coin_y)

    async def get_lp_supply(
            self,
            lp_addr: int):
        try:
            lp_contract = self.get_contract(address=lp_addr,
                                            abi=self.sith_swap_contracts.pool_abi,
                                            provider=self.account)
            response = await lp_contract.functions['totalSupply'].call()
            return response.res

        except ClientError:
            logger.error(f"Can't get LP supply for {lp_addr}")
            return None

    async def build_txn_payload_data(self):
        stable = self.is_pool_stable(
            coin_x_symbol=self.coin_x.symbol,
            coin_y_symbol=self.coin_y.symbol
        )
        lp_address = await self.get_pool_for_pair(
            stable=stable,
            router_contract=self.router_contract,
            coin_x_address=self.coin_x.contract_address,
            coin_y_address=self.coin_y.contract_address
        )
        if lp_address is None:
            logger.error(f"Can't get pool for {self.coin_x.symbol.upper()} {self.coin_y.symbol.upper()}")
            return None

        lp_balance = await self.get_token_balance(
            token_address=lp_address,
            account=self.account
        )
        if lp_balance == 0:
            return None

        lp_supply = await self.get_lp_supply(lp_addr=lp_address)
        if lp_supply is None:
            return None

        sorted_pair: list = await self.get_sorted_tokens(
            pool_addr=hex(lp_address),
            pool_abi=self.sith_swap_contracts.pool_abi)
        if sorted_pair is None:
            return None

        token0_addr: int = sorted_pair[0]
        token1_addr: int = sorted_pair[1]

        reserves: dict = await self.get_reserves(
            router_contract=self.router_contract,
            coin_x_address=hex(token0_addr),
            coin_y_address=hex(token1_addr),
            stable=stable
        )
        if reserves is None:
            return None

        reserve_x = reserves[hex(token0_addr)]
        reserve_y = reserves[hex(token1_addr)]

        amount_in_x_wei, amount_in_y_wei = calc_output_burn_liquidity(
            reserve_x=reserve_x,
            reserve_y=reserve_y,
            lp_supply=lp_supply,
            to_burn=lp_balance
        )
        amount_in_x_with_slippage = int(amount_in_x_wei - (amount_in_x_wei * self.task.slippage / 100))
        amount_in_y_with_slippage = int(amount_in_y_wei - (amount_in_y_wei * self.task.slippage / 100))

        token_x_decimals = await self.get_token_decimals(
            contract_address=self.coin_x.contract_address,
            abi=self.coin_x.abi,
            provider=self.account
        )
        amount_in_x_decimals = amount_in_x_wei / 10 ** token_x_decimals

        token_y_decimals = await self.get_token_decimals(
            contract_address=self.coin_y.contract_address,
            abi=self.coin_y.abi,
            provider=self.account
        )
        amount_in_y_decimals = amount_in_y_wei / 10 ** token_y_decimals

        approve_call = self.build_token_approve_call(
            token_addr=hex(lp_address),
            spender=self.sith_swap_contracts.router_address,
            amount_wei=lp_balance
        )

        remove_liq_call = self.build_call(
            to_addr=self.router_contract.address,
            func_name='removeLiquidity',
            call_data=[
                token0_addr,
                token1_addr,
                stable,
                lp_balance,
                0,
                amount_in_x_with_slippage,
                0,
                amount_in_y_with_slippage,
                0,
                self.account.address,
                int(time.time() + 3600)
            ]
        )

        calls = [approve_call, remove_liq_call]

        return {
            'amount_x_decimals': amount_in_x_decimals,
            'amount_y_decimals': amount_in_y_decimals,
            'calls': calls
        }

    async def send_txn(self):
        amounts_out_data = await self.build_txn_payload_data()
        if amounts_out_data is None:
            return None

        txn_calls = amounts_out_data['calls']

        txn_info_message = (f"Remove Liquidity (SithSwap) | "
                            f"{round(amounts_out_data['amount_x_decimals'], 4)} ({self.coin_x.symbol.upper()}) + "
                            f"{round(amounts_out_data['amount_y_decimals'], 4)} ({self.coin_y.symbol.upper()}). "
                            f"Slippage: {self.task.slippage}%.")

        txn_status = await self.simulate_and_send_transfer_type_transaction(account=self.account,
                                                                            calls=txn_calls,
                                                                            txn_info_message=txn_info_message, )

        return txn_status
