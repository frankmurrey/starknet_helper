import random

from modules.base import StarkBase
from src.schemas.configs.avnu import AvnuSwapConfigSchema
from contracts.tokens.main import Tokens
from contracts.avnu.main import AvnuContracts

from starknet_py.net.http_client import HttpMethod
from starknet_py.net.client_errors import ClientError
from loguru import logger


class AvnuSwap(StarkBase):
    config: AvnuSwapConfigSchema

    def __init__(
            self,
            account,
            config
    ):
        super().__init__(client=account.client)

        self.account = account
        self.config = config

        self.tokens = Tokens()
        self.avnu_contracts = AvnuContracts()
        self.router_contract = self.get_contract(address=self.avnu_contracts.router_address,
                                                 abi=self.avnu_contracts.router_abi,
                                                 provider=account)

        self.coin_x = self.tokens.get_by_name(self.config.coin_to_swap)
        self.coin_y = self.tokens.get_by_name(self.config.coin_to_receive)

        self.amount_out_decimals = None
        self.amount_in_decimals = None

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

        if self.config.use_all_balance is True:
            amount_out_wei = wallet_token_balance_wei

        elif self.config.send_percent_balance is True:
            percent = random.randint(self.config.min_amount_out, self.config.max_amount_out) / 100
            amount_out_wei = int(wallet_token_balance_wei * percent)

        elif wallet_token_balance_decimals < self.config.max_amount_out:
            amount_out_wei = self.get_random_amount_out_of_token(min_amount=self.config.min_amount_out,
                                                                 max_amount=wallet_token_balance_decimals,
                                                                 decimals=token_decimals)

        else:
            amount_out_wei = self.get_random_amount_out_of_token(
                min_amount=self.config.min_amount_out,
                max_amount=self.config.max_amount_out,
                decimals=token_decimals
            )

        return amount_out_wei

    async def build_txn_payload_calls(self):
        amount_out_wei = await self.get_amount_out_from_balance()

        quotes = await self.get_quotes(amount_out_wei=amount_out_wei)
        if quotes is None:
            return None

        amount_in_wei = self.i16(quotes['buyAmount'])
        amount_in_wei_with_slippage = int(amount_in_wei * (1 - (self.config.slippage / 100)))

        exchange_address = quotes['routes'][0]['address']

        token_x_decimals = await self.get_token_decimals(contract_address=self.coin_x.contract_address,
                                                         abi=self.coin_x.abi,
                                                         provider=self.account)
        self.amount_out_decimals = amount_out_wei / 10 ** token_x_decimals
        token_y_decimals = await self.get_token_decimals(contract_address=self.coin_y.contract_address,
                                                         abi=self.coin_y.abi,
                                                         provider=self.account)
        self.amount_in_decimals = amount_in_wei_with_slippage / 10 ** token_y_decimals

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

        return calls

    async def send_swap_txn(self):
        txn_payload_calls = await self.build_txn_payload_calls()
        if txn_payload_calls is None:
            return False

        txn_info_message = (f"Swap (Avnu) | {round(self.amount_out_decimals, 4)} ({self.coin_x.symbol.upper()}) -> "
                            f"{round(self.amount_in_decimals, 4)} ({self.coin_y.symbol.upper()}). "
                            f"Slippage: {self.config.slippage}%.")

        txn_status = await self.simulate_and_send_transfer_type_transaction(account=self.account,
                                                                            calls=txn_payload_calls,
                                                                            txn_info_message=txn_info_message,
                                                                            config=self.config)

        return txn_status
