import time
from typing import Union
from typing import TYPE_CHECKING

from loguru import logger
from starknet_py.net.client_errors import ClientError

from modules.base import LiquidityModuleBase
from modules.myswap.base import MySwapBase
from modules.myswap.math import calc_output_burn_liquidity
from src.schemas.action_models import ModuleExecutionResult, TransactionPayloadData
from utils.get_delay import get_delay

if TYPE_CHECKING:
    from src.schemas.tasks.myswap import MySwapAddLiquidityTask
    from src.schemas.tasks.myswap import MySwapRemoveLiquidityTask
    from src.schemas.wallet_data import WalletData


class MySwapAddLiquidity(MySwapBase, LiquidityModuleBase):

    task: 'MySwapAddLiquidityTask'

    def __init__(
            self,
            account,
            task: 'MySwapAddLiquidityTask',
            wallet_data: 'WalletData',
    ):
        super().__init__(
            account=account,
            task=task,
            wallet_data=wallet_data,
        )

        self.task = task

    async def get_amounts_out(self) -> Union[dict, None]:
        """
        Calculate amount out for coin_x and coin_y using reserves data
        :return:
        """
        amount_out_x_wei = await self.calculate_amount_out_from_balance(coin_x=self.coin_x,)
        if amount_out_x_wei is None:
            self.log_error(f"Failed to calculate amount out for {self.coin_x.symbol.upper()}")
            return None

        reserves_data = await self.get_pool_reserves_data(
            coin_x_symbol=self.task.coin_x,
            coin_y_symbol=self.task.coin_y,
            router_contract=self.router_contract
        )
        if reserves_data is None:
            self.log_error(
                f"Failed to get reserves data for pair {self.coin_x.symbol.upper()}/{self.coin_y.symbol.upper()}"
            )
            return None

        amount_out_y_wei_and_fee = await self.get_amount_in_and_dao_fee(
            reserves_data=reserves_data,
            amount_out_wei=amount_out_x_wei,
            coin_x_obj=self.coin_x,
            coin_y_obj=self.coin_y
        )

        if amount_out_y_wei_and_fee is None:
            self.log_error(
                f"Failed to calculate amount out for {self.coin_y.symbol.upper()}"
            )
            return None

        return {
            self.coin_x.contract_address: amount_out_x_wei,
            self.coin_y.contract_address: amount_out_y_wei_and_fee[0]
        }

    async def build_txn_payload_data(self) -> Union[TransactionPayloadData, None]:
        """
        Build transaction payload data
        :return:
        """
        pool_id = self.get_pool_id(
            coin_x_symbol=self.coin_x.symbol,
            coin_y_symbol=self.coin_y.symbol
        )
        if pool_id is None:
            self.log_error(
                f"Failed to get pool id for pair {self.coin_x.symbol.upper()}/{self.coin_y.symbol.upper()}"
            )
            return None

        token_pair = await self.get_token_pair_for_pool(pool_id=pool_id)
        if token_pair is None:
            self.log_error(f"Failed to get token pair for pool id {pool_id}")
            return None

        token0_address, token1_address = token_pair

        if self.i16(token0_address) == self.i16(self.coin_x.contract_address):
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

            reserves_data = await self.get_pool_reserves_data(
                coin_x_symbol=self.coin_x.symbol,
                coin_y_symbol=self.coin_y.symbol,
                router_contract=self.router_contract
            )
            if reserves_data is None:
                self.log_error(
                    f"Failed to get reserves data for pair {self.coin_x.symbol.upper()}/{self.coin_y.symbol.upper()}"
                )
                return None

            amount1_wei_and_dao_fee = await self.get_amount_in_and_dao_fee(
                reserves_data=reserves_data,
                amount_out_wei=amount0_wei,
                coin_x_obj=self.coin_x,
                coin_y_obj=self.coin_y,
            )
            if amount1_wei_and_dao_fee is None:
                self.log_error(
                    f"Failed to calculate amount out for {self.coin_y.symbol.upper()}"
                )
                return None

            amount1_wei, dao_fee = amount1_wei_and_dao_fee

            if amount1_wei > self.initial_balance_y_wei:
                self.log_error(
                    f"Amount out {self.coin_y.symbol.upper()} ({amount1_wei / 10 ** self.token_y_decimals}) "
                    f"is greater than actual balance: {self.initial_balance_y_wei / 10 ** self.token_y_decimals}"
                )
                return None

        else:
            amount1_wei = await self.calculate_amount_out_from_balance(coin_x=self.coin_y)
            if amount1_wei is None:
                self.log_error(f'Failed to calculate amount out for {self.coin_y.symbol.upper()}')
                return None

            if amount1_wei > self.initial_balance_x_wei:
                self.log_error(
                    f"Amount out {self.coin_y.symbol.upper()} ({amount1_wei / 10 ** self.token_y_decimals}) "
                    f"is greater than actual balance: {self.initial_balance_x_wei / 10 ** self.token_y_decimals}"
                )
                return None

            reserves_data = await self.get_pool_reserves_data(
                coin_x_symbol=self.coin_x.symbol,
                coin_y_symbol=self.coin_y.symbol,
                router_contract=self.router_contract
            )
            if reserves_data is None:
                self.log_error(
                    f"Failed to get reserves data for pair {self.coin_y.symbol.upper()}/{self.coin_x.symbol.upper()}"
                )
                return None

            amount0_wei_and_dao_fee = await self.get_amount_in_and_dao_fee(
                reserves_data=reserves_data,
                amount_out_wei=amount1_wei,
                coin_x_obj=self.coin_x,
                coin_y_obj=self.coin_y,
            )
            if amount0_wei_and_dao_fee is None:
                self.log_error(
                    f"Failed to calculate amount out for {self.coin_x.symbol.upper()}"
                )
                return None

            amount0_wei, dao_fee = amount0_wei_and_dao_fee

            if amount0_wei > self.initial_balance_y_wei:
                self.log_error(
                    f"Amount out {self.coin_x.symbol.upper()} ({amount0_wei / 10 ** self.token_x_decimals}) "
                    f"is greater than actual balance: {self.initial_balance_y_wei / 10 ** self.token_x_decimals}"
                )
                return None

            self.coin_x, self.coin_y = self.coin_y, self.coin_x
            self.token_x_decimals, self.token_y_decimals = self.token_y_decimals, self.token_x_decimals

        amount0_with_slippage = int(amount0_wei * (1 - self.task.slippage / 100))
        amount1_with_slippage = int(amount1_wei * (1 - self.task.slippage / 100))

        approve_call_0 = self.build_token_approve_call(
            token_addr=token_pair[0],
            spender=hex(self.router_contract.address),
            amount_wei=amount0_wei
        )
        approve_call_1 = self.build_token_approve_call(
            token_addr=token_pair[1],
            spender=hex(self.router_contract.address),
            amount_wei=amount1_wei
        )

        add_liq_call = self.build_call(
            to_addr=self.router_contract.address,
            func_name='add_liquidity',
            call_data=[
                self.i16(token_pair[0]),
                amount0_wei,
                0,
                amount0_with_slippage,
                0,
                self.i16(token_pair[1]),
                amount1_wei,
                0,
                amount1_with_slippage,
                0
            ]
        )

        calls = [approve_call_0, approve_call_1, add_liq_call]

        return TransactionPayloadData(
            calls=calls,
            amount_x_decimals=amount0_wei / 10 ** self.token_x_decimals,
            amount_y_decimals=amount1_wei / 10 ** self.token_y_decimals
        )


class MySwapRemoveLiquidity(MySwapBase, LiquidityModuleBase):

    task: 'MySwapRemoveLiquidityTask'

    def __init__(
            self,
            account,
            task: 'MySwapRemoveLiquidityTask',
            wallet_data: 'WalletData',
    ):
        super().__init__(
            account=account,
            task=task,
            wallet_data=wallet_data,
        )

        self.account = account
        self.task = task

    def get_lp_token_address_for_pool(
            self,
            token_0_symbol,
            token_1_symbol
    ) -> Union[str, None]:
        """
        Get LP token address for pool from token name
        :param token_0_symbol:
        :param token_1_symbol:
        :return:
        """
        lp_symbol = f"msw_{token_0_symbol.lower()}_{token_1_symbol.lower()}"
        lp_token_address = self.tokens.get_by_name(lp_symbol).contract_address

        return lp_token_address

    async def get_lp_supply(
            self,
            lp_addr
    ) -> Union[int, None]:
        """
        Get LP token supply
        :param lp_addr:
        :return:
        """
        try:
            call = self.build_call(
                to_addr=lp_addr,
                func_name='totalSupply',
                call_data=[]
            )
            resp = await self.account.client.call_contract(call)
            return resp[0]

        except ClientError:
            self.log_error(f"Failed to get LP supply")
            return None

    async def get_amounts_out(
            self,
            token0_address: str,
            token1_address: str,
            lp_token_address: str,
            lp_amount_out_wei: int
    ) -> Union[dict, None]:
        """
        Calculate amount out for coin_x and coin_y using reserves data
        :param token0_address:
        :param token1_address:
        :param lp_token_address:
        :param lp_amount_out_wei:
        :return:
        """

        reserves_data = await self.get_pool_reserves_data(
            coin_x_symbol=self.task.coin_x,
            coin_y_symbol=self.task.coin_y,
            router_contract=self.router_contract
        )
        if reserves_data is None:
            self.log_error(
                f"Failed to get reserves data for pair {self.task.coin_x.upper()}/{self.task.coin_y.upper()}"
            )
            return None

        lp_supply = await self.get_lp_supply(lp_addr=lp_token_address)
        if lp_supply is None:
            self.log_error(f"Failed to get LP supply")
            return None

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

    async def build_txn_payload_data(self) -> Union[TransactionPayloadData, None]:
        """
        Build transaction payload data for remove liquidity
        :return:
        """

        pool_id = self.get_pool_id(
            coin_x_symbol=self.task.coin_x,
            coin_y_symbol=self.task.coin_y
        )
        if pool_id is None:
            self.log_error(
                f"Failed to get pool id for pair {self.task.coin_x.upper()}/{self.task.coin_y.upper()}"
            )
            return None

        lp_token_address = self.get_lp_token_address_for_pool(
            token_0_symbol=self.pools[pool_id][0],
            token_1_symbol=self.pools[pool_id][1]
        )
        if lp_token_address is None:
            self.log_error(f"Failed to get LP token address for pool id {pool_id}")
            return None

        wallet_lp_balance_wei = await self.get_token_balance_for_address(
            token_address=self.i16(lp_token_address),
            account=self.account,
            address=self.account.address
        )
        if wallet_lp_balance_wei == 0:
            self.log_error(f"Wallet LP balance = 0")
            return None

        token_pair: list[str, str] = await self.get_token_pair_for_pool(pool_id=pool_id)
        if token_pair is None:
            self.log_error(f"Failed to get token pair for pool id {pool_id}")
            return None

        amounts_out: dict = await self.get_amounts_out(
            token0_address=token_pair[0],
            token1_address=token_pair[1],
            lp_token_address=lp_token_address,
            lp_amount_out_wei=wallet_lp_balance_wei
        )
        if amounts_out is None:
            self.log_error(f"Failed to calculate amounts out")
            return None

        amount_out_0_with_slippage = int(amounts_out[token_pair[0]] * (1 - self.task.slippage / 100))
        amount_out_1_with_slippage = int(amounts_out[token_pair[1]] * (1 - self.task.slippage / 100))

        approve_call = self.build_token_approve_call(
            token_addr=lp_token_address,
            spender=hex(self.router_contract.address),
            amount_wei=wallet_lp_balance_wei
        )

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

        token_0_decimals = await self.get_tokens_decimals_by_call(
            token_address=self.i16(token_pair[0]),
            account=self.account
        )
        amount_out_x_decimals = amounts_out[self.coin_x.contract_address] / 10 ** token_0_decimals

        token_1_decimals = await self.get_tokens_decimals_by_call(
            token_address=self.i16(token_pair[1]),
            account=self.account
        )
        amount_out_1_decimals = amounts_out[self.coin_y.contract_address] / 10 ** token_1_decimals

        calls = [approve_call, remove_liq_call]

        return TransactionPayloadData(
            calls=calls,
            token_pair_0=amount_out_x_decimals,
            token_pair_1=amount_out_1_decimals
        )
