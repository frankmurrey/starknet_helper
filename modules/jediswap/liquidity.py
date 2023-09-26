import time
from typing import Union
from typing import TYPE_CHECKING

from loguru import logger
from starknet_py.net.client_errors import ClientError

from modules.jediswap.base import JediSwapBase
from modules.jediswap.math import get_lp_burn_output

if TYPE_CHECKING:
    from src.schemas.tasks.jediswap import JediSwapAddLiquidityTask
    from src.schemas.tasks.jediswap import JediSwapRemoveLiquidityTask


class JediSwapAddLiquidity(JediSwapBase):
    task: 'JediSwapAddLiquidityTask'

    def __init__(
            self,
            account,
            task: 'JediSwapAddLiquidityTask'
    ):

        super().__init__(
            account=account,
            task=task,
        )

        self.task = task
        self.account = account

    async def build_txn_payload_calls(self) -> Union[dict, None]:
        """
        Build the transaction payload calls for the add liquidity type transaction.
        :return:
        """
        amount_x_out_wei = await self.calculate_amount_out_from_balance(coin_x=self.coin_x)
        if amount_x_out_wei is None:
            return None

        amount_x_out_wei_with_slippage = int(amount_x_out_wei * (1 - (self.task.slippage / 100)))

        if amount_x_out_wei > self.initial_balance_x_wei:
            logger.error(f"Amount out {self.coin_x.symbol.upper()} ({amount_x_out_wei / 10 ** self.token_x_decimals}) "
                         f"is greater than actual balance: {self.initial_balance_x_wei / 10 ** self.token_x_decimals}")
            return None

        amount_y_out_wei: int = await self.get_amount_in(
            amount_out_wei=amount_x_out_wei,
            coin_x_obj=self.coin_x,
            coin_y_obj=self.coin_y,
            router_contract=self.router_contract
        )
        if amount_y_out_wei is None:
            return None
        amount_y_out_wei_with_slippage = int(amount_y_out_wei * (1 - (self.task.slippage / 100)))

        if amount_y_out_wei > self.initial_balance_y_wei:
            logger.error(f"Amount out {self.coin_y.symbol.upper()} ({amount_y_out_wei / 10 ** self.token_y_decimals}) "
                         f"is greater than actual balance: {self.initial_balance_y_wei / 10 ** self.token_y_decimals}")
            return None

        txn_deadline = int(time.time() + 3600)

        approve_x_call = self.build_token_approve_call(
            token_addr=self.coin_x.contract_address,
            spender=hex(self.router_contract.address),
            amount_wei=int(amount_x_out_wei)
        )

        approve_y_call = self.build_token_approve_call(
            token_addr=self.coin_y.contract_address,
            spender=hex(self.router_contract.address),
            amount_wei=int(amount_y_out_wei)
        )

        add_liq_call = self.build_call(
            to_addr=self.router_contract.address,
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
            ]
        )

        calls = [approve_x_call, approve_y_call, add_liq_call]

        return {
            'calls': calls,
            'amount_x_decimals': amount_x_out_wei / 10 ** self.token_x_decimals,
            'amount_y_decimals': amount_y_out_wei / 10 ** self.token_y_decimals,
        }

    async def send_txn(self) -> bool:
        """
        Send the add liquidity transaction.
        :return:
        """
        await self.set_fetched_tokens_data()

        if self.check_local_tokens_data() is False:
            return False

        txn_payload_data = await self.build_txn_payload_calls()
        if txn_payload_data is None:
            return False

        txn_info_message = (
            f"Add Liquidity (JediSwap) | "
            f"{round(txn_payload_data['amount_x_decimals'], 5)} ({self.coin_x.symbol.upper()}) "
            f"+ {round(txn_payload_data['amount_y_decimals'], 5)} ({self.coin_y.symbol.upper()}). "
            f"Slippage: {self.task.slippage}%."
        )

        txn_status = await self.simulate_and_send_transfer_type_transaction(
            account=self.account,
            calls=txn_payload_data['calls'],
            txn_info_message=txn_info_message
        )

        return txn_status


class JediSwapRemoveLiquidity(JediSwapBase):
    task: 'JediSwapRemoveLiquidityTask'

    def __init__(
            self,
            account,
            task: 'JediSwapRemoveLiquidityTask'
    ):
        super().__init__(
            account=account,
            task=task,
        )

        self.task = task
        self.account = account

    async def get_pool_address(self) -> Union[int, None]:
        """
        Get the liquidity pool address for the coin pair.
        :return:
        """
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

        except ClientError:
            logger.error(f"Error while getting pool address")
            return None

    async def get_lp_supply(
            self,
            lp_addr
    ) -> Union[int, None]:
        """
        Get the LP token supply.
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
            logger.error(f"Error while getting LP supply")
            return None

    async def get_token_0_in_pool(self,
                                  pool_addr) -> Union[int, None]:
        """
        Get the token 0 address in the pool.
        :param pool_addr:
        :return:
        """
        try:
            call = self.build_call(
                to_addr=pool_addr,
                func_name='token0',
                call_data=[]
            )
            resp = await self.account.client.call_contract(call)
            return resp[0]

        except ClientError:
            logger.error(f"Error while getting token 0 address in the pool")
            return None

    async def get_token_1_in_pool(
            self,
            pool_addr
    ) -> Union[int, None]:
        """
        Get the token 1 address in the pool.
        :param pool_addr:
        :return:
        """
        try:
            call = self.build_call(
                to_addr=pool_addr,
                func_name='token1',
                call_data=[]
            )
            resp = await self.account.client.call_contract(call)
            return resp[0]

        except ClientError:
            logger.error(f"Error while getting token 1 address in the pool")
            return None

    async def get_amounts_out(
            self,
            pool_addr,
            lp_amount_out_wei: int
    ) -> Union[tuple, None]:
        """
        Get the amount of tokens out for the given LP amount out using formula.
        :param pool_addr:
        :param lp_amount_out_wei:
        :return:
        """
        token0_addr = await self.get_token_0_in_pool(pool_addr=pool_addr)
        token1_addr = await self.get_token_1_in_pool(pool_addr=pool_addr)
        if token0_addr is None or token1_addr is None:
            return None

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
        if pool_token0_balance is None or pool_token1_balance is None:
            return None

        lp_supply = await self.get_lp_supply(lp_addr=pool_addr)
        if lp_supply is None:
            return None

        output: tuple = get_lp_burn_output(
            amount_to_burn=lp_amount_out_wei,
            total_supply=lp_supply,
            contract_balance_x=pool_token0_balance,
            contract_balance_y=pool_token1_balance
        )
        return output

    async def build_txn_payload_data(self) -> Union[dict, None]:
        """
        Build the transaction payload data for the remove liquidity type transaction.
        :return:
        """
        pool_addr = await self.get_pool_address()
        if pool_addr is None:
            return None

        wallet_lp_balance = await self.get_token_balance(
            token_address=pool_addr,
            account=self.account
        )

        if wallet_lp_balance == 0:
            logger.error(f"Wallet LP ({self.coin_x.symbol.upper()} + {self.coin_y.symbol.upper()}) balance = 0")
            return None

        amounts_out: tuple = await self.get_amounts_out(
            pool_addr=pool_addr,
            lp_amount_out_wei=wallet_lp_balance
        )
        if amounts_out is None:
            return None

        approve_call = self.build_token_approve_call(
            token_addr=hex(pool_addr),
            spender=hex(self.router_contract.address),
            amount_wei=int(wallet_lp_balance)
        )

        amount_x_out_wei = amounts_out[0]
        amount_y_out_wei = amounts_out[1]

        amount_x_out_with_slippage = int(amount_x_out_wei * (1 - (self.task.slippage / 100)))
        amount_y_out_with_slippage = int(amount_y_out_wei * (1 - (self.task.slippage / 100)))

        dead_line = int(time.time() + 3600)

        remove_liq_call = self.build_call(
            to_addr=self.router_contract.address,
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
            ]
        )

        calls = [approve_call, remove_liq_call]

        return {
            'calls': calls,
            'amount_x_decimals': amount_x_out_wei / 10 ** self.token_x_decimals,
            'amount_y_decimals': amount_y_out_wei / 10 ** self.token_y_decimals,
        }

    async def send_txn(self) -> bool:
        """
        Send the remove liquidity transaction.
        :return:
        """
        await self.set_fetched_tokens_data()

        if self.check_local_tokens_data() is False:
            return False

        txn_payload_data = await self.build_txn_payload_data()
        if txn_payload_data is None:
            return False

        txn_info_message = (
            f"Remove Liquidity (JediSwap). "
            f"{round(txn_payload_data['amount_x_decimals'], 3)} {self.coin_x.symbol.upper()} + "
            f"{round(txn_payload_data['amount_y_decimals'], 3)} {self.coin_y.symbol.upper()}. "
            f"Slippage: {self.task.slippage}%."
        )

        txn_status = await self.simulate_and_send_transfer_type_transaction(
            account=self.account,
            calls=txn_payload_data['calls'],
            txn_info_message=txn_info_message
        )

        return txn_status
