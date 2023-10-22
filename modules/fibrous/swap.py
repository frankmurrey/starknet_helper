import time
from typing import Union
from typing import TYPE_CHECKING

from starknet_py.net.account.account import Account
from starknet_py.net.http_client import HttpMethod
from starknet_py.net.client_errors import ClientError
from loguru import logger

from modules.jediswap.base import JediSwapBase
from modules.base import SwapModuleBase
from src.schemas.action_models import ModuleExecutionResult, TransactionPayloadData
from utils.get_delay import get_delay
from contracts.fibrous.main import FibrousContracts


if TYPE_CHECKING:
    from src.schemas.tasks.fibrous import FibrousSwapTask


class FibrousSwap(SwapModuleBase):
    task: 'FibrousSwapTask'
    account: Account

    def __init__(
            self,
            account,
            task: 'FibrousSwapTask',
    ):
        super().__init__(
            account=account,
            task=task,
        )

        self.task = task
        self.account = account

        self.fibrous_contracts = FibrousContracts()
        self.router_contract = self.get_contract(
            address=self.fibrous_contracts.router_address,
            abi=self.fibrous_contracts.router_abi,
            provider=account
        )

    async def get_execute_data(self, amount_out_wei: int) -> list:
        url = "https://api.fibrous.finance/execute"

        payload = {
            "tokenInAddress": self.coin_x.contract_address,
            "tokenOutAddress": self.coin_y.contract_address,
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
            logger.error("Failed to get swap data")
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
            return None

        approve_call = self.build_token_approve_call(
            token_addr=self.coin_x.contract_address,
            spender=hex(self.router_contract.address),
            amount_wei=int(amount_x_wei)
        )

        payload = await self.get_execute_data(amount_out_wei=amount_x_wei)
        if payload is None:
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
        pass

    async def send_txn(self) -> ModuleExecutionResult:
        """
        Send swap type transaction
        :return:
        """
        await self.set_fetched_tokens_data()

        if self.check_local_tokens_data() is False:
            self.module_execution_result.execution_info = f"Failed to fetch local tokens data"
            return self.module_execution_result

        txn_payload_data = await self.build_txn_payload_data()
        if txn_payload_data is None:
            self.module_execution_result.execution_info = f"Failed to build transaction payload data"
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
                self.module_execution_result.execution_info = f"Failed to build reverse transaction payload data"
                return self.module_execution_result

            reverse_txn_status = await self.send_swap_type_txn(
                account=self.account,
                txn_payload_data=reverse_txn_payload_data
            )

            return reverse_txn_status

        return txn_status
