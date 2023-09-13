import random
from typing import Union
from typing import TYPE_CHECKING

from starknet_py.net.http_client import HttpMethod
from starknet_py.net.client_errors import ClientError
from loguru import logger

from modules.base import SwapModuleBase
from contracts.tokens.main import Tokens
from contracts.avnu.main import AvnuContracts

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
            client=account.client,
            task=task,
        )

        self.account = account
        self.task = task

        self.tokens = Tokens()
        self.avnu_contracts = AvnuContracts()
        self.router_contract = self.get_contract(address=self.avnu_contracts.router_address,
                                                 abi=self.avnu_contracts.router_abi,
                                                 provider=account)

        self.coin_x = self.tokens.get_by_name(self.task.coin_to_swap)
        self.coin_y = self.tokens.get_by_name(self.task.coin_to_receive)

    async def get_quotes(
            self,
            amount_out_wei: int,
    ):

        url = "http://starknet.api.avnu.fi/swap/v1/quotes"

        payload = {
            "sellTokenAddress": self.coin_x.contract_address,
            "buyTokenAddress": self.coin_y.contract_address,
            "sellAmount": hex(amount_out_wei),
            "takerAddress": hex(self.account.address),
            "size": 3,
            "integratorName": "AVNU Portal"
        }

        try:
            response = await self.account.client._client._make_request(session=self.account.client._client.session,
                                                                       address=url,
                                                                       http_method=HttpMethod.GET,
                                                                       payload=None,
                                                                       params=payload)

            return response[0]
        except ClientError:
            logger.error(f"Failed to get quotes")
            return None

    async def get_amount_out_from_balance(self):
        wallet_token_balance_wei = await self.get_token_balance(token_address=self.coin_x.contract_address,
                                                                account=self.account)

        if wallet_token_balance_wei == 0:
            logger.error(f"Wallet {self.coin_x.symbol.upper()} balance = 0")
            return None

        token_decimals = await self.get_token_decimals(contract_address=self.coin_x.contract_address,
                                                       abi=self.coin_x.abi,
                                                       provider=self.account)

        wallet_token_balance_decimals = wallet_token_balance_wei / 10 ** token_decimals

        if self.task.use_all_balance is True:
            amount_out_wei = wallet_token_balance_wei

        elif self.task.send_percent_balance is True:
            percent = random.randint(int(self.task.min_amount_out), int(self.task.max_amount_out)) / 100
            amount_out_wei = int(wallet_token_balance_wei * percent)

        elif wallet_token_balance_decimals < self.task.max_amount_out:
            amount_out_wei = self.get_random_amount_out_of_token(min_amount=self.task.min_amount_out,
                                                                 max_amount=wallet_token_balance_decimals,
                                                                 decimals=token_decimals)

        else:
            amount_out_wei = self.get_random_amount_out_of_token(
                min_amount=self.task.min_amount_out,
                max_amount=self.task.max_amount_out,
                decimals=token_decimals
            )

        return amount_out_wei

    async def build_txn_payload_data(self) -> Union[dict, None]:
        amount_out_wei = await self.get_amount_out_from_balance()

        quotes = await self.get_quotes(amount_out_wei=amount_out_wei)
        if quotes is None:
            return None

        amount_in_wei = self.i16(quotes['buyAmount'])
        amount_in_wei_with_slippage = int(amount_in_wei * (1 - (self.task.slippage / 100)))

        exchange_address = quotes['routes'][0]['address']

        token_x_decimals = await self.get_token_decimals(contract_address=self.coin_x.contract_address,
                                                         abi=self.coin_x.abi,
                                                         provider=self.account)
        amount_x_decimals = amount_out_wei / 10 ** token_x_decimals

        token_y_decimals = await self.get_token_decimals(contract_address=self.coin_y.contract_address,
                                                         abi=self.coin_y.abi,
                                                         provider=self.account)
        amount_y_decimals = amount_in_wei / 10 ** token_y_decimals

        approve_call = self.build_token_approve_call(token_addr=self.coin_x.contract_address,
                                                     spender=hex(self.router_contract.address),
                                                     amount_wei=int(amount_out_wei))

        swap_call = self.build_call(to_addr=self.router_contract.address,
                                    func_name='multi_route_swap',
                                    call_data=[self.i16(self.coin_x.contract_address),
                                               amount_out_wei,
                                               0,
                                               self.i16(self.coin_y.contract_address),
                                               int(amount_in_wei),
                                               0,
                                               int(amount_in_wei_with_slippage),
                                               0,
                                               self.account.address,
                                               0,
                                               0,
                                               1,
                                               self.i16(self.coin_x.contract_address),
                                               self.i16(self.coin_y.contract_address),
                                               self.i16(exchange_address),
                                               100
                                               ])

        calls = [approve_call, swap_call]

        return {
            'calls': calls,
            'amount_x_decimals': amount_x_decimals,
            'amount_y_decimals': amount_y_decimals,
        }

    async def send_txn(self):
        txn_payload_data = await self.build_txn_payload_data()
        if txn_payload_data is None:
            return False

        txn_status = await self.send_swap_type_txn(
            account=self.account,
            txn_payload_data=txn_payload_data
        )

        return txn_status
