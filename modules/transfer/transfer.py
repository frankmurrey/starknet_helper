import random
from typing import TYPE_CHECKING, Union

from starknet_py.net.client_errors import ClientError

import config
from modules.base import ModuleBase
from src.schemas.wallet_data import WalletData
from contracts.tokens.main import Tokens
from src.schemas.action_models import ModuleExecutionResult

if TYPE_CHECKING:
    from src.schemas.tasks.transfer import TransferTask


class Transfer(ModuleBase):
    def __init__(
            self,
            account,
            wallet_data: WalletData,
            task: 'TransferTask',
    ):

        super().__init__(
            account=account,
            task=task,
            wallet_data=wallet_data
        )

        self.account = account
        self.wallet_data = wallet_data
        self.task = task

        self.tokens = Tokens()

        self.coin_x = self.tokens.get_by_name(self.task.coin_x)
        self.coin_x_contract = self.get_contract(
            address=self.coin_x.contract_address,
            abi=self.coin_x.abi,
            provider=self.account
        )

        self.initial_balance_x_wei = None
        self.coin_x_decimals = None

    async def set_fetched_tokens_data(self):
        """
        Fetches initial balances and token decimals for both tokens.
        :return:
        """
        self.initial_balance_x_wei = await self.get_token_balance(
            token_address=self.coin_x.contract_address,
            account=self.account
        )

        self.coin_x_decimals = await self.get_token_decimals(
            contract_address=self.coin_x.contract_address,
            abi=self.coin_x.abi,
            provider=self.account
        )

    def check_local_tokens_data(self) -> bool:
        """
        Checks if token decimals are fetched.
        :return:
        """
        if self.initial_balance_x_wei is None and self.coin_x_decimals is None:
            self.log_error(f"Token {self.coin_x.symbol.upper()} decimals not fetched")
            return False

    async def estimate_eth_transfer_fee(self) -> Union[int, None]:
        """
        Estimate the ETH transfer fee.
        :return:
        """
        try:
            eth = self.tokens.get_by_name('eth')
            eth_contract = self.get_contract(
                address=eth.contract_address,
                abi=eth.abi,
                provider=self.account
            )

            transfer_call = self.build_call(
                to_addr=eth_contract.address,
                func_name='transfer',
                call_data=[
                    self.account.address,
                    int(1e9),
                    0
                ]
            )

            cairo_version = await self.get_cairo_version_for_txn_execution(account=self.account)
            signed_invoke_transaction = await self.sign_invoke_transaction(
                calls=[transfer_call],
                account=self.account,
                cairo_version=cairo_version
            )
            if signed_invoke_transaction is None:
                self.log_error(f"Error while signing invoke transaction")
                return None

            estimate_transaction = await self.get_estimated_transaction_fee(
                account=self.account,
                transaction=signed_invoke_transaction
            )

            return estimate_transaction

        except ClientError:
            self.log_error(f"Error while estimating ETH transfer fee")
            return None

    def calculate_amount_out_from_balance(self) -> Union[int, None]:
        """
        Calculate the amount out from the balance of the coin x.
        :return:
        """

        if self.initial_balance_x_wei == 0:
            self.log_error(f"Wallet {self.coin_x.symbol.upper()} balance = 0")
            return None

        if self.coin_x_decimals is None:
            self.log_error(f"Token {self.coin_x.symbol.upper()} decimals not fetched")
            return None

        wallet_token_x_balance_decimals = self.initial_balance_x_wei / 10 ** self.coin_x_decimals

        if self.task.use_all_balance is True:
            amount_out_wei = self.initial_balance_x_wei

        elif self.task.send_percent_balance is True:
            percent = random.randint(int(self.task.min_amount_out), int(self.task.max_amount_out)) / 100
            amount_out_wei = int(self.initial_balance_x_wei * percent)

        elif wallet_token_x_balance_decimals < self.task.min_amount_out:
            self.log_error(
                f"Wallet {self.coin_x.symbol.upper()} balance less than min amount out, "
                f"balance: {wallet_token_x_balance_decimals}, min amount out: {self.task.min_amount_out}"
            )
            return None

        elif wallet_token_x_balance_decimals < self.task.max_amount_out:
            amount_out_wei = self.get_random_amount_out_of_token(
                min_amount=self.task.min_amount_out,
                max_amount=wallet_token_x_balance_decimals,
                decimals=self.coin_x_decimals
            )

        else:
            amount_out_wei = self.get_random_amount_out_of_token(
                min_amount=self.task.min_amount_out,
                max_amount=self.task.max_amount_out,
                decimals=self.coin_x_decimals
            )

        return amount_out_wei

    async def build_txn_payload_data(self) -> Union[dict, None]:
        """
        Build the transaction payload data.
        :return:
        """
        if self.wallet_data.pair_address is None:
            self.log_error(f"Pair address not set")
            return None

        if len(self.wallet_data.pair_address) != config.STARK_KEY_LENGTH:
            self.log_error(f"Pair address is not valid")
            return None

        amount_out_wei = self.calculate_amount_out_from_balance()
        if amount_out_wei is None:
            self.log_error(f"Error while calculating amount out for {self.coin_x.symbol.upper()}")
            return None

        if self.coin_x.symbol.upper() == 'ETH':
            if self.task.use_all_balance is True:
                eth_transfer_fee = await self.estimate_eth_transfer_fee()
                if eth_transfer_fee is None:
                    self.log_error(f"Error while estimating ETH transfer fee")
                    return None

                amount_out_wei -= int(eth_transfer_fee * 1.8)

        recipient_address = self.wallet_data.pair_address
        transfer_call = self.build_call(
            to_addr=self.coin_x_contract.address,
            func_name='transfer',
            call_data=[
                self.i16(recipient_address),
                amount_out_wei,
                0
            ]
        )

        return {
            "calls": [transfer_call],
            "amount_x_decimals": amount_out_wei / 10 ** self.coin_x_decimals
        }

    async def send_txn(self) -> ModuleExecutionResult:
        """
        Send the transaction. Implements the abstract method from the base 'ModuleBase' class.
        :return:
        """
        await self.set_fetched_tokens_data()

        if self.check_local_tokens_data() is False:
            self.log_error(f"Failed to fetch local tokens data")
            return self.module_execution_result

        payload_data = await self.build_txn_payload_data()
        if payload_data is None:
            self.log_error(f"Failed to build transaction payload data")
            return self.module_execution_result

        txn_info_message = (
            f"Transfer {round(payload_data['amount_x_decimals'], 4)} {self.coin_x.symbol.upper()}, "
            f"recipient: {self.wallet_data.pair_address}"
        )

        txn_status = await self.simulate_and_send_transfer_type_transaction(
            account=self.account,
            calls=payload_data['calls'],
            txn_info_message=txn_info_message
        )

        return txn_status
