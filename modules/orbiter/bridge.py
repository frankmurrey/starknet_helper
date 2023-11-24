import time
import random
from typing import Union
from typing import TYPE_CHECKING

from starknet_py.net.http_client import HttpMethod
from starknet_py.net.client_errors import ClientError
from loguru import logger

import config
from modules.base import ModuleBase
from contracts.orbiter.main import OrbiterContracts
from contracts.chains.main import Chains
from contracts.base import TokenBase
from src.schemas.action_models import ModuleExecutionResult, TransactionPayloadData
from utils.orbiter_utils import get_orbiter_bridge_data_by_token

if TYPE_CHECKING:
    from src.schemas.tasks.orbiter import OrbiterBridgeTask
    from src.schemas.wallet_data import WalletData


class OrbiterBridge(ModuleBase):
    task: 'OrbiterBridgeTask'

    def __init__(
            self,
            account,
            task: 'OrbiterBridgeTask',
            wallet_data: 'WalletData'
    ):
        super().__init__(
            account=account,
            task=task,
        )

        self.task = task
        self.wallet_data = wallet_data
        self.coin_x = self.tokens.get_by_name(self.task.coin_x)

        self.chains = Chains()
        self.dst_chain = self.chains.get_by_name(self.task.dst_chain)
        self.chain_data = get_orbiter_bridge_data_by_token(
            token_symbol=self.coin_x.symbol,
            chain_id=self.dst_chain.orbiter_id
        )

        self.orbiter_contracts = OrbiterContracts()
        self.router_contract = self.get_contract(
            address=self.orbiter_contracts.router_address,
            abi=self.orbiter_contracts.router_abi,
            provider=account
        )

        self.initial_balance_x_wei = None
        self.token_x_decimals = None

    async def get_tokens_data(self) -> Union[list, None]:
        url = "https://api3.loopring.io/api/v3/exchange/tokens"

        try:
            response = await self.account.client._client._make_request(
                session=self.account.client._client.session,
                address=url,
                http_method=HttpMethod.GET,
                payload=None,
                params=None
            )

            return response

        except ClientError:
            logger.error(f"Failed to get tokens data")
            return None

    async def get_token_data(self, token_symbol: str) -> Union[dict, None]:
        tokens_data = await self.get_tokens_data()
        if not tokens_data:
            logger.error(f"Failed to get tokens data")
            return None

        for token_data in tokens_data:
            if token_data["symbol"] == token_symbol.upper():
                return token_data

        logger.error(f"Failed to get token data for {token_symbol.upper()}")
        return None

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
        token_x_decimals = await self.get_token_decimals(
            contract_address=self.coin_x.contract_address,
            abi=self.coin_x.abi,
            provider=self.account
        )
        if balance_x_wei == 0:
            logger.error(f"Wallet {coin_x.symbol.upper()} balance = 0")
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
            logger.error(
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
        self.token_x_decimals = token_x_decimals

        return amount_out_wei

    async def build_txn_payload_data(self) -> Union[TransactionPayloadData, None]:
        """
        Builds transaction payload data
        :return:
        """
        if self.wallet_data.pair_address is None:
            logger.error(f"Pair EVM address not set")
            return None

        if len(self.wallet_data.pair_address) != config.EVM_ADDRESS_LENGTH:
            logger.error(f"Pair EVM address is not valid, should be {config.EVM_ADDRESS_LENGTH} chars length")
            return None

        amount_out_wei = await self.calculate_amount_out_from_balance(self.coin_x)
        if not amount_out_wei:
            logger.error(f"Failed to calculate amount out")
            return None

        amount_out_wei_fee_removed = amount_out_wei - self.chain_data.tradingFee * 10 ** self.token_x_decimals

        min_price_wei = self.chain_data.minPrice * 10 ** self.token_x_decimals
        max_price_wei = self.chain_data.maxPrice * 10 ** self.token_x_decimals

        if amount_out_wei_fee_removed < min_price_wei:
            logger.error(
                f"Amount out less than min amount out: "
                f"Min: {self.chain_data.minPrice} {self.coin_x.symbol.upper()}, "
                f"Amount out after fee: {amount_out_wei_fee_removed / 10 ** self.token_x_decimals} "
                f"{self.coin_x.symbol.upper()}, Fee: {self.chain_data.tradingFee} {self.coin_x.symbol.upper()}"
            )
            return None

        if amount_out_wei_fee_removed > max_price_wei:
            logger.error(
                f"Amount out more than max amount out: "
                f"Max: {self.chain_data.maxPrice} {self.coin_x.symbol.upper()}, "
                f"Amount out after fee: {amount_out_wei_fee_removed / 10 ** self.token_x_decimals} "
                f"{self.coin_x.symbol.upper()}, Fee: {self.chain_data.tradingFee} {self.coin_x.symbol.upper()}"
            )
            return None

        subtrahend = 20000
        value_after_subtrahend = amount_out_wei - subtrahend
        amount_out_wei = (value_after_subtrahend // 10000 * 10000) + self.dst_chain.orbiter_id

        approve_call = self.build_token_approve_call(
            token_addr=self.coin_x.contract_address,
            spender=hex(self.router_contract.address),
            amount_wei=int(amount_out_wei)
        )

        transfer_address = self.chain_data.makerAddress

        bridge_call = self.build_call(
            to_addr=self.router_contract.address,
            func_name='transferERC20',
            call_data=[
                self.i16(self.coin_x.contract_address),
                self.i16(transfer_address),
                amount_out_wei,
                0,
                self.i16(self.wallet_data.pair_address),
            ]
        )

        return TransactionPayloadData(
            calls=[approve_call, bridge_call],
            amount_x_decimals=amount_out_wei / 10 ** self.token_x_decimals,
            amount_y_decimals=amount_out_wei / 10 ** self.token_x_decimals - self.chain_data.tradingFee,
        )

    async def send_txn(self) -> ModuleExecutionResult:
        """
        Sends transaction.
        :return:
        """
        txn_payload_data = await self.build_txn_payload_data()
        if txn_payload_data is None:
            self.module_execution_result.execution_info = f"Failed to build txn payload data"
            return self.module_execution_result

        txn_info_message = (
            f"Bridge {self.coin_x.symbol.upper()} Stark → {self.dst_chain.name.upper()} (Orbiter) - "
            f"Out: {round(txn_payload_data.amount_x_decimals, 4)}, "
            f"To receive: {round(txn_payload_data.amount_y_decimals, 4)}, "
            f"Fee: {self.chain_data.tradingFee}, "
            f"recipient: {self.wallet_data.pair_address}"
        )

        txn_status = await self.simulate_and_send_transfer_type_transaction(
            account=self.account,
            calls=txn_payload_data.calls,
            txn_info_message=txn_info_message
        )

        return txn_status
