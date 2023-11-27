import time
from typing import Union
from typing import Tuple
from typing import TYPE_CHECKING
from decimal import Decimal

from loguru import logger

from modules.base import LiquidityModuleBase
from modules.k10swap.base import K10SwapBase
from modules.k10swap.math import get_liquidity_value
from src.schemas.action_models import ModuleExecutionResult, TransactionPayloadData
from utils.get_delay import get_delay

if TYPE_CHECKING:
    from src.schemas.tasks.k10swap import K10SwapAddLiquidityTask
    from src.schemas.tasks.k10swap import K10SwapRemoveLiquidityTask
    from src.schemas.wallet_data import WalletData


class K10SwapAddLiquidity(K10SwapBase, LiquidityModuleBase):
    task = 'K10SwapAddLiquidityTask'

    def __init__(
            self,
            account,
            task: 'K10SwapAddLiquidityTask',
            wallet_data: 'WalletData',
    ):
        super().__init__(
            account=account,
            task=task,
            wallet_data=wallet_data,
        )
        self.task = task
        self.account = account

    async def build_txn_payload_data(self) -> Union[TransactionPayloadData, None]:
        """
        Build the transaction payload data for the add liquidity type transaction.
        :return:
        """
        pool_address = await self.get_token_pair_address(
            coin_x=self.coin_x,
            coin_y=self.coin_y
        )
        if pool_address is None:
            self.log_error(f'Failed to get pool address for {self.coin_x.symbol.upper()}-{self.coin_y.symbol.upper()}')
            return None

        token_pair = await self.get_token_pair(token_pair_address=pool_address)
        if token_pair is None:
            self.log_error(f'Failed to get token pair for {self.coin_x.symbol.upper()}-{self.coin_y.symbol.upper()}')
            return None

        token0_address, token1_address = token_pair

        if token0_address == self.i16(self.coin_x.contract_address):
            amount0_wei = await self.calculate_amount_out_from_balance(coin_x=self.coin_x)
            if amount0_wei is None:
                self.log_error(f'Failed to calculate amount out for {self.coin_x.symbol.upper()}')
                return None

            if amount0_wei > self.initial_balance_x_wei:
                self.log_error(
                    f"Amount out {self.coin_x.symbol.upper()} ({amount0_wei / 10 ** self.token_x_decimals}) "
                    f"is greater than actual balance: {self.initial_balance_x_wei / 10 ** self.token_x_decimals}"
                )
                return None

            amount1_wei = await self.get_amounts_in(
                amount_in_wei=amount0_wei,
                coin_x=self.coin_x,
                coin_y=self.coin_y,
            )
            if amount1_wei is None:
                self.log_error(f'Failed to calculate amount in for {self.coin_y.symbol.upper()}')
                return None

            amount1_wei = amount1_wei.amounts[1]

            if amount1_wei > self.initial_balance_y_wei:
                self.log_error(
                    f"Amount out {self.coin_y.symbol.upper()} ({amount1_wei / 10 ** self.token_y_decimals}) "
                    f"is greater than actual balance: {self.initial_balance_y_wei / 10 ** self.token_y_decimals}"
                )
                return None

        else:

            amount1_wei = await self.calculate_amount_out_from_balance(coin_x=self.coin_x)
            if amount1_wei is None:
                self.log_error(f'Failed to calculate amount out for {self.coin_x.symbol.upper()}')
                return None

            if amount1_wei > self.initial_balance_x_wei:
                self.log_error(
                    f"Amount out {self.coin_x.symbol.upper()} ({amount1_wei / 10 ** self.token_x_decimals}) "
                    f"is greater than actual balance: {self.initial_balance_x_wei / 10 ** self.token_x_decimals}"
                )
                return None

            amount0_wei = await self.get_amounts_in(
                amount_in_wei=amount1_wei,
                coin_x=self.coin_x,
                coin_y=self.coin_y,
            )
            if amount0_wei is None:
                self.log_error(f'Failed to calculate amount in for {self.coin_y.symbol.upper()}')
                return None

            amount0_wei = amount0_wei.amounts[1]
            self.coin_x, self.coin_y = self.coin_y, self.coin_x
            self.token_x_decimals, self.token_y_decimals = self.token_y_decimals, self.token_x_decimals

        amount_0_wei_with_slippage = int(amount0_wei * (1 - (self.task.slippage / 100)))
        amount_1_wei_with_slippage = int(amount1_wei * (1 - (self.task.slippage / 100)))

        txn_deadline = int(time.time() + 3600)

        approve_call_0 = self.build_token_approve_call(
            token_addr=self.coin_x.contract_address,
            spender=hex(self.router_contract.address),
            amount_wei=int(amount0_wei)
        )

        approve_call_1 = self.build_token_approve_call(
            token_addr=self.coin_y.contract_address,
            spender=hex(self.router_contract.address),
            amount_wei=int(amount1_wei)
        )

        add_liquidity_call = self.build_call(
            to_addr=self.router_contract.address,
            func_name='addLiquidity',
            call_data=[
                self.i16(self.coin_x.contract_address),
                self.i16(self.coin_y.contract_address),
                amount0_wei,
                0,
                amount1_wei,
                0,
                amount_0_wei_with_slippage,
                0,
                amount_1_wei_with_slippage,
                0,
                self.account.address,
                txn_deadline
            ]
        )

        calls = [approve_call_0, approve_call_1, add_liquidity_call]

        return TransactionPayloadData(
            calls=calls,
            amount_x_decimals=amount0_wei / 10 ** self.token_x_decimals,
            amount_y_decimals=amount1_wei / 10 ** self.token_y_decimals
        )


class K10SwapRemoveLiquidity(K10SwapBase, LiquidityModuleBase):
    task = 'K10SwapRemoveLiquidityTask'

    def __init__(
            self,
            account,
            task: 'K10SwapRemoveLiquidityTask',
            wallet_data: 'WalletData',

    ):
        super().__init__(
            account=account,
            task=task,
            wallet_data=wallet_data,
        )
        self.task = task
        self.account = account

    async def get_lp_supply(
            self,
            lp_address: str
    ) -> Union[int, None]:
        """
        Get the LP supply.
        :param lp_address:
        :return:
        """
        try:
            call = self.build_call(
                to_addr=self.i16(lp_address),
                func_name='totalSupply',
                call_data=[]
            )
            resp = await self.account.client.call_contract(call)

            return resp[0]

        except Exception as ex:
            self.log_error(f"Error while getting LP supply")
            return None

    async def get_reserves(
            self,
            pair_address: int
    ) -> Union[Tuple[int, int], None]:
        """
        Get the reserves for the given pair address.
        :param pair_address:
        :return:
        """
        try:
            call = self.build_call(
                to_addr=pair_address,
                func_name='getReserves',
                call_data=[]
            )
            resp = await self.account.client.call_contract(call)

            return resp[0], resp[1]

        except Exception as ex:
            self.log_error(f"Error while getting reserves")
            return None

    async def get_amounts_out(
            self,
            pair_address: int,
            reserve_x: int,
            reserve_y: int,
            lp_amount_out_wei: int
    ) -> Union[Tuple[Decimal, Decimal], None]:
        """
        Get the amounts out for the given pair address.
        :param pair_address:
        :param reserve_x:
        :param reserve_y:
        :param lp_amount_out_wei:
        :return:
        """
        try:
            lp_supply = await self.get_lp_supply(lp_address=hex(pair_address))
            if lp_supply is None:
                return None

            output = get_liquidity_value(
                total_supply=lp_supply,
                liquidity=lp_amount_out_wei,
                reserve_x=reserve_x,
                reserve_y=reserve_y
            )

            return output

        except Exception as ex:
            self.log_error(f"Error while getting amounts out")
            return None

    async def build_txn_payload_data(self) -> Union[TransactionPayloadData, None]:
        """
        Build the transaction payload data for the remove liquidity type transaction.
        :return:
        """
        pair_address = await self.get_token_pair_address(
            coin_x=self.coin_x,
            coin_y=self.coin_y
        )
        if pair_address is None:
            self.log_error(f'Failed to get pair address for {self.coin_x.symbol.upper()}-{self.coin_y.symbol.upper()}')
            return None

        token_pair = await self.get_token_pair(token_pair_address=pair_address)
        if token_pair is None:
            self.log_error(f'Failed to get token pair for {self.coin_x.symbol.upper()}-{self.coin_y.symbol.upper()}')
            return None

        reserves = await self.get_reserves(pair_address=pair_address)
        if reserves is None:
            self.log_error(f'Failed to get reserves for {self.coin_x.symbol.upper()}-{self.coin_y.symbol.upper()}')
            return None

        wallet_lp_balance = await self.get_token_balance(
            token_address=pair_address,
            account=self.account
        )
        if wallet_lp_balance == 0:
            self.log_error(f"Wallet LP ({self.coin_x.symbol.upper()} + {self.coin_y.symbol.upper()}) balance = 0")
            return None

        amounts_out = await self.get_amounts_out(
            pair_address=pair_address,
            lp_amount_out_wei=wallet_lp_balance,
            reserve_x=reserves[0],
            reserve_y=reserves[1]
        )
        if amounts_out is None:
            self.log_error(f'Failed to get amounts out for {self.coin_x.symbol.upper()}-{self.coin_y.symbol.upper()}')
            return None

        approve_call = self.build_token_approve_call(
            token_addr=hex(pair_address),
            spender=hex(self.router_contract.address),
            amount_wei=int(wallet_lp_balance)
        )

        amount_x_out_wei = int(amounts_out[0])
        amount_y_out_wei = int(amounts_out[1])

        amount_in_x_wei_with_slippage = int(amount_x_out_wei * (1 - (self.task.slippage / 100)))
        amount_in_y_wei_with_slippage = int(amount_y_out_wei * (1 - (self.task.slippage / 100)))

        dead_line = int(time.time() + 3600)

        remove_liq_call = self.build_call(
            to_addr=self.router_contract.address,
            func_name='removeLiquidity',
            call_data=[
                token_pair[0],
                token_pair[1],
                int(wallet_lp_balance),
                0,
                amount_in_x_wei_with_slippage,
                0,
                amount_in_y_wei_with_slippage,
                0,
                self.account.address,
                dead_line
            ]
        )

        calls = [approve_call, remove_liq_call]

        return TransactionPayloadData(
            calls=calls,
            amount_x_decimals=amount_x_out_wei / 10 ** self.token_x_decimals,
            amount_y_decimals=amount_y_out_wei / 10 ** self.token_y_decimals
        )
