from typing import Union
from typing import TYPE_CHECKING

from starknet_py.net.account.account import Account
from starknet_py.net.http_client import HttpMethod
from starknet_py.net.client_errors import ClientError
from loguru import logger

from modules.base import SwapModuleBase
from src.schemas.action_models import TransactionPayloadData
from contracts.fibrous.main import FibrousContracts


if TYPE_CHECKING:
    from src.schemas.tasks.fibrous import FibrousSwapTask
    from src.schemas.wallet_data import WalletData


class FibrousSwap(SwapModuleBase):
    task: 'FibrousSwapTask'
    account: Account

    def __init__(
            self,
            account,
            wallet_data: 'WalletData',
            task: 'FibrousSwapTask',
    ):
        super().__init__(
            account=account,
            task=task,
            wallet_data=wallet_data,
        )

        self.task = task
        self.account = account

        self.fibrous_contracts = FibrousContracts()
        self.router_contract = self.get_contract(
            address=self.fibrous_contracts.router_address,
            abi=self.fibrous_contracts.router_abi,
            provider=account
        )

    async def get_execute_data(
            self,
            amount_out_wei: int,
            coin_x_address: str,
            coin_y_address: str,
    ) -> list:
        url = "https://api.fibrous.finance/execute"

        payload = {
            "tokenInAddress": coin_x_address,
            "tokenOutAddress": coin_y_address,
            "amount": hex(amount_out_wei),
            "slippage": self.task.slippage / 100,
            "destination": hex(self.account.address),
        }

        response = await self.account.client._client._make_request(
            session=self.account.client._client.session,
            address=url,
            http_method=HttpMethod.GET,
            payload=None,
            params=payload
        )

        return response

    async def get_swap_data(self, amount_out_wei: int) -> Union[dict, None]:
        """
        Fetches token swap quotes from Fibrous API
        :param amount_out_wei:
        :return:
        """
        try:
            url = "https://api.fibrous.finance/route"

            payload = {
                "tokenInAddress": self.coin_x.contract_address,
                "tokenOutAddress": self.coin_y.contract_address,
                "amount": hex(amount_out_wei),
            }

            response = await self.account.client._client._make_request(
                session=self.account.client._client.session,
                address=url,
                http_method=HttpMethod.GET,
                payload=None,
                params=payload
            )

            return response

        except ClientError:
            self.log_error("Failed to get swap data")
            return None

    def _i16(self, value) -> int:
        try:
            return int(value, 16)
        except TypeError:
            return int(value)

    def rebuild_payload(self, payload: list) -> list:
        new_payload = []
        for value in payload:
            if isinstance(value, str):
                if value.startswith('0x'):
                    new_payload.append(self.i16(value))
                else:
                    new_payload.append(int(value))
            else:
                new_payload.append(value)

        return new_payload

    async def build_txn_payload_data(self) -> Union[TransactionPayloadData, None]:
        """
        Builds transaction payload data
        :return:
        """

        amount_x_wei = await self.calculate_amount_out_from_balance(coin_x=self.coin_x)
        if amount_x_wei is None:
            self.log_error(
                f"Failed to calculate amount out for {self.coin_x.symbol.upper()} -> {self.coin_y.symbol.upper()}"
            )
            return None

        approve_call = self.build_token_approve_call(
            token_addr=self.coin_x.contract_address,
            spender=hex(self.router_contract.address),
            amount_wei=int(amount_x_wei)
        )

        payload = await self.get_execute_data(
            amount_out_wei=amount_x_wei,
            coin_x_address=self.coin_x.contract_address,
            coin_y_address=self.coin_y.contract_address,
        )
        if payload is None:
            self.log_error(
                f"Failed to get execute data for {self.coin_x.symbol.upper()} -> {self.coin_y.symbol.upper()}"
            )
            return None

        payload_decoded = self.rebuild_payload(payload)

        amount_y_wei = payload_decoded[4] * 100 / (100 - self.task.slippage)

        swap_call = self.build_call(
            to_addr=self.router_contract.address,
            func_name='swap',
            call_data=payload_decoded
        )

        calls = [approve_call, swap_call]
        return TransactionPayloadData(
            calls=calls,
            amount_x_decimals=amount_x_wei / 10 ** self.token_x_decimals,
            amount_y_decimals=amount_y_wei / 10 ** self.token_y_decimals
        )

    async def build_reverse_txn_payload_data(self) -> Union[TransactionPayloadData, None]:
        """
        Builds reverse transaction payload data
        :return:
        """
        wallet_y_balance_wei = await self.get_token_balance(
            token_address=self.coin_y.contract_address,
            account=self.account
        )

        if wallet_y_balance_wei == 0:
            self.log_error(f"Wallet {self.coin_y.symbol.upper()} balance = 0")
            return None

        amount_out_y_wei = wallet_y_balance_wei - self.initial_balance_y_wei
        if amount_out_y_wei <= 0:
            self.log_error(f"Wallet {self.coin_y.symbol.upper()} balance less than initial balance")
            return None

        approve_call = self.build_token_approve_call(
            token_addr=self.coin_y.contract_address,
            spender=hex(self.router_contract.address),
            amount_wei=int(amount_out_y_wei)
        )

        payload = await self.get_execute_data(
            amount_out_wei=amount_out_y_wei,
            coin_x_address=self.coin_y.contract_address,
            coin_y_address=self.coin_x.contract_address,
        )
        if payload is None:
            self.log_error(
                f"Failed to get execute data for {self.coin_y.symbol.upper()} -> {self.coin_x.symbol.upper()}"
            )
            return None

        payload_decoded = self.rebuild_payload(payload)
        amount_x_wei = payload_decoded[4] * 100 / (100 - self.task.slippage)

        swap_call = self.build_call(
            to_addr=self.router_contract.address,
            func_name='swap',
            call_data=payload_decoded
        )

        calls = [approve_call, swap_call]
        return TransactionPayloadData(
            calls=calls,
            amount_x_decimals=amount_out_y_wei / 10 ** self.token_y_decimals,
            amount_y_decimals=amount_x_wei / 10 ** self.token_x_decimals
        )
