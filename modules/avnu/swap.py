import time
from typing import Union
from typing import TYPE_CHECKING

from starknet_py.net.http_client import HttpMethod
from starknet_py.net.client_errors import ClientError
from loguru import logger

from modules.base import SwapModuleBase
from contracts.avnu.main import AvnuContracts
from contracts.base import TokenBase
from utils.get_delay import get_delay
from src.schemas.action_models import ModuleExecutionResult, TransactionPayloadData

if TYPE_CHECKING:
    from src.schemas.tasks.avnu import AvnuSwapTask


class AvnuSwap(SwapModuleBase):
    task: 'AvnuSwapTask'

    def __init__(
            self,
            account,
            task: 'AvnuSwapTask'
    ):

        super().__init__(
            account=account,
            task=task,
        )

        self.task = task

        self.avnu_contracts = AvnuContracts()
        self.router_contract = self.get_contract(
            address=self.avnu_contracts.router_address,
            abi=self.avnu_contracts.router_abi,
            provider=account
        )

    async def get_quotes(
            self,
            coin_x: TokenBase,
            coin_y: TokenBase,
            amount_out_wei: int,
    ) -> Union[dict, None]:

        """
        Fetches token swap quotes from Avnu API
        :param coin_x:
        :param coin_y:
        :param amount_out_wei:
        :return:
        """

        payload = {
            "sellTokenAddress": coin_x.contract_address,
            "buyTokenAddress": coin_y.contract_address,
            "sellAmount": hex(amount_out_wei),
            "takerAddress": hex(self.account.address),
            "size": 3,
            "integratorName": "AVNU Portal"
        }

        try:
            response = await self.account.client._client._make_request(
                session=self.account.client._client.session,
                address="https://starknet.api.avnu.fi/swap/v1/quotes",
                http_method=HttpMethod.GET,
                payload=None,
                params=payload
            )

            return response[0]

        except ClientError:
            logger.error(f"Failed to get quotes, try to change IP address")
            return None

    async def build_call_data(
            self,
            quote_id: str,
            slippage: float,
            taker_address: str,
    ):
        """
        Builds call data for swap type transaction using Avnu API
        :param quote_id:
        :param slippage:
        :param taker_address:
        :return:
        """

        payload = {
            "quoteId": quote_id,
            "slippage": slippage,
            "takerAddress": taker_address
        }
        try:
            response = await self.account.client._client._make_request(
                session=self.account.client._client.session,
                address="https://starknet.api.avnu.fi/swap/v1/build",
                http_method=HttpMethod.POST,
                payload=payload,
                params=payload
            )

            return response['calldata']

        except ClientError:
            logger.error(f"Failed to get call data")
            return None

    async def build_txn_payload_data(self) -> Union[TransactionPayloadData, None]:
        """
        Builds payload data for swap type transaction
        :return:
        """
        amount_out_wei = await self.calculate_amount_out_from_balance(
            coin_x=self.coin_x,
        )
        if amount_out_wei is None:
            return None

        quotes = await self.get_quotes(
            amount_out_wei=amount_out_wei,
            coin_x=self.coin_x,
            coin_y=self.coin_y,
        )
        if quotes is None:
            return None

        call_data = await self.build_call_data(
            quote_id=quotes['quoteId'],
            slippage=int(quotes['routes'][0]['percent']),
            taker_address=hex(self.account.address)
        )
        call_data_decoded = [self.i16(x) for x in call_data]

        amount_in_wei = self.i16(quotes['buyAmount'])

        approve_call = self.build_token_approve_call(token_addr=self.coin_x.contract_address,
                                                     spender=hex(self.router_contract.address),
                                                     amount_wei=int(amount_out_wei))

        swap_call = self.build_call(to_addr=self.router_contract.address,
                                    func_name='multi_route_swap',
                                    call_data=call_data_decoded)

        return TransactionPayloadData(
            calls=[approve_call, swap_call],
            amount_x_decimals=amount_out_wei / 10 ** self.token_x_decimals,
            amount_y_decimals=amount_in_wei / 10 ** self.token_y_decimals,
        )

    async def build_reverse_txn_payload_data(self) -> Union[TransactionPayloadData, None]:
        """
        Builds payload data for reverse swap type transaction, if reverse action is enabled in task
        :return:
        """
        actual_wallet_y_balance_wei = await self.get_token_balance(
            token_address=self.coin_y.contract_address,
            account=self.account
        )

        if actual_wallet_y_balance_wei == 0:
            logger.error(f"Wallet {self.coin_y.symbol.upper()} balance = 0")
            return None

        amount_out_wei = actual_wallet_y_balance_wei - self.initial_balance_y_wei
        if amount_out_wei <= 0:
            logger.error(f"Wallet {self.coin_y.symbol.upper()} balance = 0")
            return None

        quotes = await self.get_quotes(
            amount_out_wei=amount_out_wei,
            coin_x=self.coin_y,
            coin_y=self.coin_x,
        )
        if quotes is None:
            return None

        amount_in_wei = self.i16(quotes['buyAmount'])
        amount_in_wei_with_slippage = int(amount_in_wei * (1 - (self.task.slippage / 100)))

        exchange_address = quotes['routes'][0]['address']

        approve_call = self.build_token_approve_call(token_addr=self.coin_y.contract_address,
                                                     spender=hex(self.router_contract.address),
                                                     amount_wei=int(amount_out_wei))

        swap_call = self.build_call(to_addr=self.router_contract.address,
                                    func_name='multi_route_swap',
                                    call_data=[self.i16(self.coin_y.contract_address),
                                               amount_out_wei,
                                               0,
                                               self.i16(self.coin_x.contract_address),
                                               int(amount_in_wei),
                                               0,
                                               int(amount_in_wei_with_slippage),
                                               0,
                                               self.account.address,
                                               0,
                                               0,
                                               1,
                                               self.i16(self.coin_y.contract_address),
                                               self.i16(self.coin_x.contract_address),
                                               self.i16(exchange_address),
                                               100
                                               ]
                                    )

        return TransactionPayloadData(
            calls=[approve_call, swap_call],
            amount_x_decimals=amount_out_wei / 10 ** self.token_y_decimals,
            amount_y_decimals=amount_out_wei / 10 ** self.token_x_decimals,
        )

    async def send_txn(self) -> ModuleExecutionResult:
        """
        Sends swap type transaction, if reverse action is enabled in task, sends reverse swap type transaction
        :return:
        """
        await self.set_fetched_tokens_data()

        if self.check_local_tokens_data() is False:
            self.module_execution_result.execution_info = f"Failed to fetch local tokens data"
            return self.module_execution_result

        txn_payload_data = await self.build_txn_payload_data()
        if txn_payload_data is None:
            self.module_execution_result.execution_info = f"Failed to build txn payload data"
            return self.module_execution_result

        txn_status = await self.send_swap_type_txn(
            account=self.account,
            txn_payload_data=txn_payload_data
        )
        if txn_status is False:
            self.module_execution_result.execution_info = f"Failed to send swap type txn"
            return self.module_execution_result

        if self.task.reverse_action is True:
            delay = get_delay(self.task.min_delay_sec, self.task.max_delay_sec)
            logger.info(f"Waiting {delay} seconds before reverse action")
            time.sleep(delay)

            reverse_txn_payload_data = await self.build_reverse_txn_payload_data()
            if reverse_txn_payload_data is None:
                self.module_execution_result.execution_info = f"Failed to build reverse txn payload data"
                return self.module_execution_result

            reverse_txn_status = await self.send_swap_type_txn(
                account=self.account,
                txn_payload_data=reverse_txn_payload_data,
                is_reverse=True
            )

            if reverse_txn_status is False:
                self.module_execution_result.execution_info = f"Failed to send reverse swap type txn"
                return self.module_execution_result

            return reverse_txn_status

        return txn_status
