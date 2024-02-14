from typing import Union
from typing import TYPE_CHECKING

from starknet_py.net.http_client import HttpMethod
from starknet_py.net.client_errors import ClientError

from modules.base import SwapModuleBase
from contracts.avnu.main import AvnuContracts
from contracts.base import TokenBase
from src.schemas.action_models import TransactionPayloadData

if TYPE_CHECKING:
    from src.schemas.tasks.avnu import AvnuSwapTask
    from src.schemas.wallet_data import WalletData


class AvnuSwap(SwapModuleBase):
    task: 'AvnuSwapTask'

    def __init__(
            self,
            account,
            wallet_data: 'WalletData',
            task: 'AvnuSwapTask'
    ):

        super().__init__(
            account=account,
            task=task,
            wallet_data=wallet_data,
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
            self.log_error('Failed to get quotes for {coin_x.symbol.upper()} -> {coin_y.symbol.upper()}')
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
            self.log_error(
                f'Failed to build call data for {self.coin_x.symbol.upper()} -> {self.coin_y.symbol.upper()}'
            )
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
            self.log_error(
                f"Failed to calculate amount out for"
                f" {self.coin_x.symbol.upper()} -> {self.coin_y.symbol.upper()}."
            )
            return None

        quotes = await self.get_quotes(
            amount_out_wei=amount_out_wei,
            coin_x=self.coin_x,
            coin_y=self.coin_y,
        )
        if quotes is None:
            self.log_error(f'Failed to get quotes for {self.coin_x.symbol.upper()} -> {self.coin_y.symbol.upper()})')
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
            self.log_error(f"Wallet {self.coin_y.symbol.upper()} balance = 0")
            return None

        amount_out_wei = actual_wallet_y_balance_wei - self.initial_balance_y_wei
        if amount_out_wei <= 0:
            self.log_error(f"Wallet {self.coin_y.symbol.upper()} balance = 0")
            return None

        quotes = await self.get_quotes(
            amount_out_wei=amount_out_wei,
            coin_x=self.coin_y,
            coin_y=self.coin_x,
        )
        if quotes is None:
            self.log_error(f'Failed to get quotes for {self.coin_y.symbol.upper()} -> {self.coin_x.symbol.upper()})')
            return None

        call_data = await self.build_call_data(
            quote_id=quotes['quoteId'],
            slippage=int(quotes['routes'][0]['percent']),
            taker_address=hex(self.account.address)
        )
        call_data_decoded = [self.i16(x) for x in call_data]

        amount_in_wei = self.i16(quotes['buyAmount'])

        approve_call = self.build_token_approve_call(token_addr=self.coin_y.contract_address,
                                                     spender=hex(self.router_contract.address),
                                                     amount_wei=int(amount_out_wei))

        swap_call = self.build_call(
            to_addr=self.router_contract.address,
            func_name='multi_route_swap',
            call_data=call_data_decoded
        )

        return TransactionPayloadData(
            calls=[approve_call, swap_call],
            amount_x_decimals=amount_out_wei / 10 ** self.token_y_decimals,
            amount_y_decimals=amount_in_wei / 10 ** self.token_x_decimals,
        )
