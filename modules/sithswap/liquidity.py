import time
from typing import TYPE_CHECKING, Union

from loguru import logger
from starknet_py.net.client_errors import ClientError
from starknet_py.net.account.account import Account

from modules.base import LiquidityModuleBase
from modules.sithswap.base import SithBase
from modules.sithswap.math import calc_output_burn_liquidity
from src.schemas.action_models import ModuleExecutionResult, TransactionPayloadData
from utils.get_delay import get_delay


if TYPE_CHECKING:
    from src.schemas.tasks.sithswap import SithSwapAddLiquidityTask
    from src.schemas.tasks.sithswap import SithSwapRemoveLiquidityTask


class SithSwapAddLiquidity(SithBase, LiquidityModuleBase):
    task: 'SithSwapAddLiquidityTask'

    def __init__(
            self,
            account,
            task: 'SithSwapAddLiquidityTask'
    ):

        super().__init__(
            account=account,
            task=task
        )

        self.task = task

    async def get_amounts_out_data(self) -> Union[dict, None]:
        """
        Get amounts out data for the add liquidity transaction.
        :return:
        """
        amount_out_x_wei = await self.calculate_amount_out_from_balance(coin_x=self.coin_x)
        if amount_out_x_wei is None:
            logger.error(f"Can't get amount out for {self.coin_x.symbol.upper()}")
            return None

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
            'amount_x_decimals': amount_out_x_wei / 10 ** self.token_x_decimals,
            'amount_y_decimals': amount_out_y_wei / 10 ** self.token_x_decimals,
            'stable': stable,
            'pool_addr': pool_addr
        }

    async def build_txn_payload_calls(self) -> Union[TransactionPayloadData, None]:
        """
        Build the transaction payload data for the add liquidity transaction.
        :return:
        """
        amounts_out_data: dict = await self.get_amounts_out_data()
        if amounts_out_data is None:
            return None

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

        return TransactionPayloadData(
            calls=calls,
            amount_x_decimals=amounts_out_data['amount_x_decimals'],
            amount_y_decimals=amounts_out_data['amount_y_decimals']
        )

    async def send_txn(self) -> ModuleExecutionResult:
        await self.set_fetched_tokens_data()

        if self.check_local_tokens_data() is False:
            self.module_execution_result.execution_info = f"Failed to fetch local tokens data"
            return self.module_execution_result

        txn_payload_data = await self.build_txn_payload_calls()
        if txn_payload_data is None:
            self.module_execution_result.execution_info = f"Failed to build transaction payload calls"
            return self.module_execution_result

        txn_status = await self.send_liquidity_type_txn(
            account=self.account,
            txn_payload_data=txn_payload_data,
        )

        if not txn_status.execution_status:
            return txn_status

        if self.task.reverse_action is True:
            delay = get_delay(self.task.min_delay_sec, self.task.max_delay_sec)
            logger.info(f"Waiting {delay} seconds before reverse action")
            time.sleep(delay)

            old_task = self.task.dict(exclude={"module_name",
                                               "module_type",
                                               "module"})
            new_task = self.task.reverse_action_task(**old_task)

            reverse_action_module = SithSwapRemoveLiquidity(
                account=self.account,
                task=new_task
            )
            reverse_txn_status = await reverse_action_module.send_txn()

            return reverse_txn_status

        return txn_status


class SithSwapRemoveLiquidity(SithBase, LiquidityModuleBase):
    task: 'SithSwapRemoveLiquidityTask'

    def __init__(
            self,
            account,
            task: 'SithSwapRemoveLiquidityTask'
    ):

        super().__init__(
            account=account,
            task=task,
        )

        self.task = task
        self.account: Account = account

    async def get_lp_supply(
            self,
            lp_addr: int
    ):
        """
        Get LP token supply.
        :param lp_addr:
        :return:
        """
        try:
            lp_contract = self.get_contract(
                address=lp_addr,
                abi=self.sith_swap_contracts.pool_abi,
                provider=self.account
            )
            response = await lp_contract.functions['totalSupply'].call()

            return response.res

        except ClientError:
            logger.error(f"Can't get LP supply for {lp_addr}")
            return None

    async def build_txn_payload_data(self) -> Union[TransactionPayloadData, None]:
        """
        Build the transaction payload data for the remove liquidity transaction.
        :return:
        """
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

        return TransactionPayloadData(
            calls=calls,
            amount_x_decimals=amount_in_x_decimals,
            amount_y_decimals=amount_in_y_decimals
        )

    async def send_txn(self) -> ModuleExecutionResult:
        await self.set_fetched_tokens_data()

        if self.check_local_tokens_data() is False:
            self.module_execution_result.execution_info = f"Failed to fetch local tokens data"
            return self.module_execution_result

        amounts_out_data = await self.build_txn_payload_data()
        if amounts_out_data is None:
            self.module_execution_result.execution_info = f"Failed to build transaction payload data"
            return self.module_execution_result

        txn_status = await self.send_liquidity_type_txn(
            account=self.account,
            txn_payload_data=amounts_out_data
        )

        return txn_status
