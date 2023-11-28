import random
from typing import Union
from typing import TYPE_CHECKING

from loguru import logger

import config
from modules.base import ModuleBase
from contracts.stark_bridge.main import StarkBridgeContracts
from contracts.base import TokenBase
from src.schemas.action_models import ModuleExecutionResult, TransactionPayloadData

if TYPE_CHECKING:
    from src.schemas.tasks.stark_bridge import StarkBridgeTask
    from src.schemas.wallet_data import WalletData


class StarkBridge(ModuleBase):
    task: 'StarkBridgeTask'

    def __init__(
            self,
            account,
            task: 'StarkBridgeTask',
            wallet_data: 'WalletData'
    ):
        super().__init__(
            account=account,
            task=task,
            wallet_data=wallet_data,
        )

        self.task = task
        self.wallet_data = wallet_data
        self.coin_x = self.tokens.get_by_name('ETH')

        self.stark_bridge_contracts = StarkBridgeContracts()
        self.router_contract = self.get_contract(
            address=self.stark_bridge_contracts.router_address,
            abi=self.stark_bridge_contracts.router_abi,
            provider=account
        )

        self.initial_balance_x_wei = None
        self.token_x_decimals = 18

    async def calculate_amount_out_from_balance(
            self,
            coin_x: TokenBase
    ) -> Union[int, None]:
        """
        Returns random amount out of token x balance.
        :param coin_x:
        :return:
        """
        balance_x_wei = await self.get_token_balance(
            token_address=self.coin_x.contract_address,
            account=self.account
        )
        token_x_decimals = self.token_x_decimals

        if balance_x_wei == 0:
            self.log_error(f"Wallet {coin_x.symbol.upper()} balance = 0")
            return None

        wallet_token_x_balance_decimals = balance_x_wei / 10 ** token_x_decimals

        if self.task.use_all_balance is True:
            amount_out_wei = balance_x_wei

        elif self.task.send_percent_balance is True:
            percent = random.randint(
                int(self.task.min_amount_out), int(self.task.max_amount_out)
            ) / 100
            amount_out_wei = int(balance_x_wei * percent)

        elif wallet_token_x_balance_decimals < self.task.min_amount_out:
            self.log_error(
                f"Wallet {coin_x.symbol.upper()} balance less than min amount out, "
                f"balance: {wallet_token_x_balance_decimals}, min amount out: {self.task.min_amount_out}"
            )
            return None

        elif wallet_token_x_balance_decimals < self.task.max_amount_out:
            amount_out_wei = self.get_random_amount_out_of_token(
                min_amount=self.task.min_amount_out,
                max_amount=wallet_token_x_balance_decimals,
                decimals=token_x_decimals
            )

        else:
            amount_out_wei = self.get_random_amount_out_of_token(
                min_amount=self.task.min_amount_out,
                max_amount=self.task.max_amount_out,
                decimals=token_x_decimals
            )

        self.initial_balance_x_wei = balance_x_wei

        return amount_out_wei

    async def build_txn_payload_data(self) -> Union[TransactionPayloadData, None]:
        """
        Builds transaction payload data
        :return:
        """

        if self.wallet_data.pair_address is None:
            self.log_error(f"Pair EVM address not set")
            return None

        if len(self.wallet_data.pair_address) != config.EVM_ADDRESS_LENGTH:
            self.log_error(f"Pair EVM address is not valid, should be {config.EVM_ADDRESS_LENGTH} chars length")
            return None

        amount_out_wei = await self.calculate_amount_out_from_balance(self.coin_x)
        if not amount_out_wei:
            self.log_error(f"Error while calculating amount out of {self.coin_x.symbol.upper()} balance")
            return None

        bridge_call = self.build_call(
            to_addr=self.router_contract.address,
            func_name='initiate_withdraw',
            call_data=[
                self.i16(self.wallet_data.pair_address),
                amount_out_wei,
                0
            ]
        )

        return TransactionPayloadData(
            calls=[bridge_call],
            amount_x_decimals=amount_out_wei / 10 ** self.token_x_decimals,
            amount_y_decimals=0,
        )

    async def send_txn(self) -> ModuleExecutionResult:
        """
        Sends transaction.
        :return:
        """
        txn_payload_data = await self.build_txn_payload_data()
        if txn_payload_data is None:
            self.log_error(f"Failed to build txn payload data")
            return self.module_execution_result

        txn_info_message = (
            f"Bridge - Stark → ETH L1 (StarkGate) of {round(txn_payload_data.amount_x_decimals, 4)} ETH, "
            f"recipient: {self.wallet_data.pair_address}"
        )

        txn_status = await self.simulate_and_send_transfer_type_transaction(
            account=self.account,
            calls=txn_payload_data.calls,
            txn_info_message=txn_info_message
        )

        return txn_status
