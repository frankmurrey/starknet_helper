import random
import time
from typing import Union
from typing import TYPE_CHECKING

from starknet_py.net.account.account import Account
from starknet_py.net.models import StarknetChainId
from starknet_py.net.models.transaction import Invoke
from starknet_py.contract import Contract
from starknet_py.net.client_errors import ClientError
from starknet_py.net.client_models import Call, TransactionReceipt
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.net.http_client import HttpMethod
from loguru import logger

from utils.key_manager.key_manager import get_key_pair_from_pk
from utils.key_manager.key_manager import get_argent_addr_from_private_key
from utils.key_manager.key_manager import get_braavos_addr_from_private_key
from src.schemas.action_models import ModuleExecutionResult
from src.gecko_pricer import GeckoPricer
from src.storage import Storage
from src import paths
from utils.file_manager import FileManager
from utils.misc import decode_wallet_version
from contracts.tokens.main import Tokens
from contracts.base import TokenBase
import config

if TYPE_CHECKING:
    from src.schemas.tasks.base.swap import SwapTaskBase
    from starknet_py.net.full_node_client import FullNodeClient
    from src.schemas.tasks.base import TaskBase


class ModuleBase:
    ETH_ADDRESS_MAINNET = '0x049D36570D4E46F48E99674BD3FCC84644DDD6B96F7C741B1562B82F9E004DC7'

    def __init__(
            self,
            client: 'FullNodeClient',
            task: 'TaskBase'
    ):

        self.client = client
        self.chain_id = StarknetChainId.MAINNET
        self.gecko_pricer = GeckoPricer(client=client)
        self.storage = Storage()
        self.tokens = Tokens()

        self.task = task
        self.module_execution_result = ModuleExecutionResult()

    def i16(self,
            hex_d: str):
        return int(hex_d, 16)

    async def get_cairo_version_for_txn_execution(
            self,
            account: Account,
    ):
        """
        Returns the Cairo version of the account contract.
        :param account:
        :return:
        """
        try:
            account_contract = await self.get_account_contract(account=account)
            version = await account_contract.functions['getVersion'].call()

            version_decoded = decode_wallet_version(version=version.version)

            major, minor, patch = version_decoded.split('.')

            if int(major) > 0 or int(minor) >= 3:
                return 1

            return 0

        except ClientError:
            return None

    async def account_deployed(
            self,
            account: Account
    ) -> bool:
        """
        Returns True if the account is deployed.
        :param account:
        :return:
        """
        version = await self.get_cairo_version_for_txn_execution(account=account)
        if version is None:
            return False

        return True

    async def get_eth_mainnet_gas_price(self) -> Union[int, None]:
        """
        Returns the current gas price on Ethereum mainnet. Rpc url is taken from the app_config.json.
        :return:
        """
        try:
            url = self.storage.app_config.eth_mainnet_rpc_url

            payload = {
                "jsonrpc": "2.0",
                "method": "eth_gasPrice",
                "params": [],
                "id": "1"
            }

            resp = await self.client._client.request(
                address=url,
                http_method=HttpMethod.POST,
                payload=payload,
                params=None
            )

            return self.i16(resp['result'])

        except ClientError:
            return None

    async def gas_price_check_loop(
            self,
            target_price_wei: int,
            time_out_sec: int,
            is_timeout_needed: bool
    ) -> tuple:
        """
        Checks the current gas price on Ethereum mainnet and waits until it is lower than the target price.
        :param is_timeout_needed:
        :param target_price_wei:
        :param time_out_sec:
        :return:
        """

        current_gas_price = await self.get_eth_mainnet_gas_price()
        if current_gas_price is None:
            logger.error(f"Error while getting gas price, waiting 1 min for rate limit to reset or change ETH RPC URL")
            time.sleep(60)

            current_gas_price = await self.get_eth_mainnet_gas_price()
            if current_gas_price is None:
                return False, current_gas_price


        if current_gas_price <= target_price_wei:
            return True, current_gas_price

        msg = f"Waiting for gas price to be lower than {target_price_wei / 10 ** 9} Gwei. "
        if is_timeout_needed is True:
            msg += f"Timeout: {time_out_sec} sec."

        logger.info(msg)

        start_time = time.time()
        delay = config.DEFAULT_DELAY_SEC
        while True:
            current_gas_price = await self.get_eth_mainnet_gas_price()
            if current_gas_price is None:
                continue

            if current_gas_price <= target_price_wei:
                return True, current_gas_price

            if is_timeout_needed is True:
                delay *= 2
                if time.time() - start_time > time_out_sec:
                    return False, current_gas_price

            time.sleep(delay)

    def get_random_amount_out_of_token(
            self,
            min_amount,
            max_amount,
            decimals: int
    ) -> int:
        """
        Returns a random amount of tokens with the specified decimals.
        :param min_amount:
        :param max_amount:
        :param decimals:
        :return:
        """
        random_amount = random.uniform(min_amount, max_amount)
        return int(random_amount * 10 ** decimals)

    def get_account_argent(
            self,
            private_key: str
    ) -> Account:
        """
        Returns an Account object for Argent wallet.
        :param private_key:
        :return:
        """
        key_pair = get_key_pair_from_pk(private_key)
        raw_address = get_argent_addr_from_private_key(private_key)

        return Account(
            address=raw_address,
            client=self.client,
            key_pair=key_pair,
            chain=self.chain_id
        )

    def get_account_braavos(
            self,
            private_key: str
    ) -> Account:
        """
        Returns an Account object for Braavos wallet.
        :param private_key:
        :return:
        """
        key_pair = get_key_pair_from_pk(private_key)
        raw_address = get_braavos_addr_from_private_key(private_key)

        return Account(
            address=raw_address,
            client=self.client,
            key_pair=key_pair,
            chain=self.chain_id
        )

    def get_contract(
            self,
            address,
            abi,
            provider
    ) -> Contract:
        """
        Returns a Contract object.
        :param address:
        :param abi:
        :param provider:
        :return:
        """
        return Contract(
            address=address,
            abi=abi,
            provider=provider
        )

    async def get_token_decimals(
            self,
            contract_address,
            abi,
            provider
    ) -> Union[int, None]:
        """
        Returns the decimals of a token.
        :param contract_address:
        :param abi:
        :param provider:
        :return:
        """
        try:
            token_contract = self.get_contract(
                address=contract_address,
                abi=abi,
                provider=provider
            )
            decimals = await token_contract.functions['decimals'].call()

            return decimals.decimals

        except Exception as e:
            logger.error(f"Error while getting token decimals: {e}")
            return None

    async def get_tokens_decimals_by_call(
            self,
            token_address: int,
            account: Account
    ) -> Union[int, None]:
        """
        Returns the decimals of a token by calling the contract.
        :param token_address:
        :param account:
        :return:
        """
        try:
            call = self.build_call(to_addr=token_address,
                                   func_name='decimals',
                                   call_data=[])
            response = await account.client.call_contract(call)
            return response[0]

        except ClientError:
            return None

    def build_call(
            self,
            to_addr: int,
            func_name: str,
            call_data: list
    ) -> Call:
        """
        Returns a Call object.
        :param to_addr:
        :param func_name:
        :param call_data:
        :return:
        """
        return Call(
            to_addr=to_addr,
            selector=get_selector_from_name(func_name),
            calldata=call_data
        )

    def build_token_approve_call(
            self,
            token_addr: str,
            amount_wei: int,
            spender: str
    ) -> Call:
        """
        Returns a Call object for approving a token.
        :param token_addr:
        :param amount_wei:
        :param spender:
        :return:
        """
        return Call(
            to_addr=self.i16(token_addr),
            selector=get_selector_from_name('approve'),
            calldata=[
                self.i16(spender),
                amount_wei,
                0
            ]
        )

    async def get_eth_balance(
            self,
            account: Account
    ) -> int:
        """
        Returns the ETH balance of an account in wei.
        :param account:
        :return:
        """
        try:
            return await account.get_balance(token_address=self.ETH_ADDRESS_MAINNET)

        except ClientError:
            return 0

    async def get_token_balance(
            self,
            account: Account,
            token_address: int
    ) -> int:
        """
        Returns the token balance of an account in wei.
        :param account:
        :param token_address:
        :return:
        """
        try:
            return await account.get_balance(token_address=token_address)

        except ClientError:
            return 0

    async def get_token_balance_for_address(
            self,
            account: Account,
            token_address: int,
            address: int
    ) -> int:
        """
        Returns the token balance of an account in wei by Call.
        :param account:
        :param token_address:
        :param address:
        :return:
        """
        try:
            call = self.build_call(
                to_addr=token_address,
                func_name='balanceOf',
                call_data=[address]
            )
            response = await account.client.call_contract(call)
            return response[0]

        except ClientError:
            return 0

    async def get_nonce(
            self,
            account: Account) -> int:
        """
        Returns the nonce of an account.
        :param account:
        :return:
        """
        try:
            return await account.get_nonce()

        except ClientError:
            return 0

    async def execute_call_transaction(
            self,
            account: Account,
            calls: list,
            max_fee: Union[int, None],
            auto_estimate: Union[bool, None],
            cairo_version: int
    ) -> tuple:
        """
        Executes a transaction.
        :param account:
        :param calls:
        :param max_fee:
        :param auto_estimate:
        :param cairo_version:
        :return: bool, response
        """
        try:
            resp = await account.execute(
                calls=calls,
                max_fee=max_fee,
                cairo_version=cairo_version,
                auto_estimate=auto_estimate
            )
            return True, resp

        except Exception as ex:

            logger.error(f"Error while executing transaction: {ex}")

            return False, None

    async def get_estimated_transaction_fee(
            self,
            account: Account,
            transaction
    ) -> Union[int, None]:
        """
        Returns the estimated transaction fee.
        :param account:
        :param transaction:
        :return:
        """
        try:
            estimate = await account.client.estimate_fee(tx=transaction)
            return estimate.overall_fee

        except ClientError:
            return None

    async def wait_for_tx_receipt(
            self,
            tx_hash: int,
            time_out_sec: int
    ) -> Union[TransactionReceipt, None]:
        """
        Waits for a transaction receipt.
        :param tx_hash:
        :param time_out_sec:
        :return:
        """
        try:
            return await self.client.wait_for_tx(
                tx_hash=tx_hash,
                check_interval=5,
                retries=(time_out_sec // 5) + 1
            )
        except Exception as ex:
            logger.error(f"Error while waiting for txn receipt: {ex}")
            return None

    async def get_account_contract(
            self,
            account: Account,
    ) -> Union[Contract, None]:
        """
        Returns the account contract.
        :param account:
        :return:
        """
        try:
            acc_abi = FileManager.read_abi_from_file(paths.ACCOUNT_ABI_FILE)
            if acc_abi is None:
                return None

            return Contract(
                address=account.address,
                abi=FileManager.read_abi_from_file(paths.ACCOUNT_ABI_FILE),
                provider=account
            )

        except ClientError:
            return None

    async def sign_invoke_transaction(
            self,
            account: Account,
            calls: list,
            cairo_version: int,
            auto_estimate: bool = False
    ) -> Union[Invoke, None]:
        try:
            return await account.sign_invoke_transaction(
                calls=calls,
                max_fee=0 if auto_estimate is False else None,
                cairo_version=cairo_version,
                auto_estimate=auto_estimate if auto_estimate is True else None
            )

        except ClientError:
            return None

    async def try_send_txn(
            self,
            retries: int = 1,
    ) -> ModuleExecutionResult:
        """
        Tries to send a transaction.
        :param retries:
        :return:
        """
        result = self.module_execution_result

        if not isinstance(retries, int):
            logger.error(f"Retries must be an integer, got {retries}, setting to 1")
            retries = 1

        for i in range(retries):
            logger.info(f"Attempt {i + 1}/{retries}")

            result = await self.send_txn()

            if result.retry_needed is False:
                return result

            if self.task.test_mode is True:
                return result

            if result.execution_status is True:
                return result

            time.sleep(1)
        else:
            logger.error(f"Failed to send txn after {retries} attempts")
            return result

    async def send_txn(self):
        """
        Abstract method for sending a transaction.
        :return:
        """
        raise NotImplementedError

    async def simulate_and_send_transfer_type_transaction(
            self,
            account: Account,
            calls: list,
            txn_info_message: str
    ) -> ModuleExecutionResult:
        """
        Simulates and sends a transfer type transaction.
        :param account:
        :param calls:
        :param txn_info_message:
        :return:
        """
        logger.warning(f"Action: {txn_info_message}")

        target_gas_price_gwei = self.storage.app_config.target_eth_mainnet_gas_price
        target_gas_price_wei = self.storage.app_config.target_eth_mainnet_gas_price * 10 ** 9
        time_out_sec = self.storage.app_config.time_to_wait_target_gas_price_sec
        is_timeout_needed = self.storage.app_config.is_gas_price_wait_timeout_needed
        gas_price_status = await self.gas_price_check_loop(
            target_price_wei=target_gas_price_wei,
            time_out_sec=time_out_sec,
            is_timeout_needed=is_timeout_needed,
        )

        status, gas_price = gas_price_status
        if gas_price is None:
            err_msg = f"Error while getting gas price. Aborting transaction."
            logger.error(err_msg)

            self.module_execution_result.execution_status = False
            self.module_execution_result.execution_info = err_msg
            return self.module_execution_result

        if status is False:
            err_msg = f"Gas price is too high ({gas_price / 10 ** 9} Gwei) after {time_out_sec}. Aborting transaction."
            logger.error(err_msg)

            self.module_execution_result.execution_status = False
            self.module_execution_result.execution_info = err_msg
            return self.module_execution_result

        logger.info(f"Gas price is under target value ({target_gas_price_gwei}), now = {gas_price / 10 ** 9} Gwei.")

        cairo_version = await self.get_cairo_version_for_txn_execution(account=account)
        if cairo_version is None:
            err_msg = "Error while getting Cairo version. Aborting transaction."
            logger.error(err_msg)

            self.module_execution_result.execution_status = False
            self.module_execution_result.execution_info = err_msg
            return self.module_execution_result

        signed_invoke_transaction = await self.sign_invoke_transaction(
            account=account,
            calls=calls,
            cairo_version=cairo_version,
            auto_estimate=not self.task.forced_gas_limit
        )
        if signed_invoke_transaction is None:
            err_msg = "Error while signing transaction. Aborting transaction."
            logger.error(err_msg)

            self.module_execution_result.execution_status = False
            self.module_execution_result.execution_info = err_msg
            return self.module_execution_result

        time.sleep(1)
        estimate_transaction = await self.get_estimated_transaction_fee(
            account=account,
            transaction=signed_invoke_transaction
        )
        if estimate_transaction is None:
            err_msg = "Transaction estimation failed."
            logger.error(f"{err_msg} Aborting transaction.")

            self.module_execution_result.execution_status = False
            self.module_execution_result.execution_info = err_msg
            return self.module_execution_result

        estimate_gas_decimals = estimate_transaction / 10 ** 18
        wallet_eth_balance = await self.get_eth_balance(account=account)
        if wallet_eth_balance is None:
            err_msg = "Error while getting wallet ETH balance. Aborting transaction."
            logger.error(err_msg)

            self.module_execution_result.execution_status = False
            self.module_execution_result.execution_info = err_msg
            return self.module_execution_result

        wallet_eth_balance_decimals = wallet_eth_balance / 10 ** 18

        if wallet_eth_balance < estimate_transaction:
            err_msg = (
                f"Insufficient ETH balance for txn fees (balance: {wallet_eth_balance_decimals}, "
                f"need {estimate_gas_decimals} ETH)"
            )
            logger.error(
                f"{err_msg}. Aborting transaction."
            )

            self.module_execution_result.execution_status = False
            self.module_execution_result.execution_info = err_msg
            return self.module_execution_result

        logger.success(
            f"Transaction estimation success, overall fee: "
            f"{estimate_gas_decimals} ETH."
        )

        max_fee = int(self.task.max_fee) if self.task.forced_gas_limit is True else None

        if self.task.test_mode is True:
            logger.info(f"Test mode enabled. Skipping transaction")
            return self.module_execution_result

        response_data = await self.execute_call_transaction(
            account=account,
            calls=calls,
            max_fee=max_fee,
            cairo_version=cairo_version,
            auto_estimate=not self.task.forced_gas_limit
        )
        response_status, response = response_data
        if response_status is False:
            err_msg = f"Error while sending txn, {response}"

            self.module_execution_result.execution_status = False
            self.module_execution_result.execution_info = err_msg
            return self.module_execution_result

        txn_hash = response.transaction_hash

        if self.task.wait_for_receipt is True:
            logger.info(
                f"Txn sent. Waiting for receipt (Timeout in {self.task.txn_wait_timeout_sec}s)."
                f" Txn Hash: {hex(txn_hash)}"
            )

            txn_receipt = await self.wait_for_tx_receipt(
                tx_hash=txn_hash,
                time_out_sec=int(self.task.txn_wait_timeout_sec)
            )
            if txn_receipt is None:
                err_msg = f"Transaction failed or not in blockchain after {self.task.txn_wait_timeout_sec}s"
                logger.error(f"{err_msg}. Txn Hash: {hex(txn_hash)}")

                self.module_execution_result.execution_status = False
                self.module_execution_result.execution_info = err_msg
                return self.module_execution_result

            txn_status = txn_receipt.execution_status.value if txn_receipt.execution_status is not None else None

            logger.success(
                f"Txn success, status: {txn_status} "
                f"(Actual fee: {txn_receipt.actual_fee / 10 ** 18}. "
                f"Txn Hash: {hex(txn_hash)})"
            )

            self.module_execution_result.execution_status = True
            self.module_execution_result.execution_info = f"Txn success, status: {txn_status}"
            self.module_execution_result.hash = hex(txn_hash)
            return self.module_execution_result

        else:
            logger.success(f"Txn sent. Txn Hash: {hex(txn_hash)}")

            self.module_execution_result.execution_status = True
            self.module_execution_result.execution_info = "Txn sent"
            self.module_execution_result.hash = hex(txn_hash)

            return self.module_execution_result


class SwapModuleBase(ModuleBase):
    task: 'SwapTaskBase'

    def __init__(
            self,
            account,
            task: 'SwapTaskBase'
    ):
        super().__init__(client=account.client, task=task)
        self._account = account

        self.coin_x = self.tokens.get_by_name(self.task.coin_x)
        self.coin_y = self.tokens.get_by_name(self.task.coin_y)

        self.initial_balance_x_wei = None
        self.initial_balance_y_wei = None

        self.token_x_decimals = None
        self.token_y_decimals = None

    async def set_fetched_tokens_data(self):
        """
        Fetches initial balances and token decimals for both tokens.
        :return:
        """
        self.initial_balance_x_wei = await self.get_token_balance(
            token_address=self.coin_x.contract_address,
            account=self._account
        )
        self.initial_balance_y_wei = await self.get_token_balance(
            token_address=self.coin_y.contract_address,
            account=self._account
        )

        self.token_x_decimals = await self.get_token_decimals(
            contract_address=self.coin_x.contract_address,
            abi=self.coin_x.abi,
            provider=self._account
        )
        self.token_y_decimals = await self.get_token_decimals(
            contract_address=self.coin_y.contract_address,
            abi=self.coin_y.abi,
            provider=self._account
        )

    def check_local_tokens_data(self) -> bool:
        """
        Checks if token decimals are fetched.
        :return:
        """
        if self.token_x_decimals is None or self.token_y_decimals is None:
            logger.error(f"Token decimals not fetched")
            return False

    async def calculate_amount_out_from_balance(
            self,
            coin_x: TokenBase
    ) -> Union[int, None]:
        """
        Returns random amount out of token x balance.
        :param coin_x:
        :return:
        """

        if self.initial_balance_x_wei == 0:
            logger.error(f"Wallet {coin_x.symbol.upper()} balance = 0")
            return None

        wallet_token_x_balance_decimals = self.initial_balance_x_wei / 10 ** self.token_x_decimals

        if self.task.use_all_balance is True:
            amount_out_wei = self.initial_balance_x_wei

        elif self.task.send_percent_balance is True:
            percent = random.randint(
                int(self.task.min_amount_out), int(self.task.max_amount_out)
            ) / 100
            amount_out_wei = int(self.initial_balance_x_wei * percent)

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
                decimals=self.token_x_decimals
            )

        else:
            amount_out_wei = self.get_random_amount_out_of_token(
                min_amount=self.task.min_amount_out,
                max_amount=self.task.max_amount_out,
                decimals=self.token_x_decimals
            )

        return amount_out_wei

    async def send_swap_type_txn(
            self,
            account: Account,
            txn_payload_data: dict,
            is_reverse: bool = False
    ) -> ModuleExecutionResult:
        """
        Sends a swap type transaction.
        :param account:
        :param txn_payload_data:
        :param is_reverse:
        :return:
        """

        self.task: 'SwapTaskBase'

        module_name = self.task.module_name.title()

        out_decimals = round(txn_payload_data['amount_x_decimals'], 4)
        in_decimals = round(txn_payload_data['amount_y_decimals'], 4)

        coin_x_symbol = self.task.coin_x.upper() if is_reverse is False else self.task.coin_x.upper()
        coin_y_symbol = self.task.coin_y.upper() if is_reverse is False else self.task.coin_y.upper()

        slippage: Union[float, int] = self.task.slippage

        txn_info_message = f"Swap ({module_name}) | " \
                           f"{out_decimals} ({coin_x_symbol}) -> " \
                           f"{in_decimals} ({coin_y_symbol}). " \
                           f"Slippage: {slippage}%."

        if self.task.compare_with_cg_price is True:
            coin_x_cg_id = self.tokens.get_cg_id_by_name(coin_x_symbol)
            coin_y_cg_id = self.tokens.get_cg_id_by_name(coin_y_symbol)
            if coin_x_cg_id is None or coin_y_cg_id is None:
                logger.error(
                    f"Error while getting CoinGecko IDs for {coin_x_symbol.upper()} and {coin_y_symbol.upper()}")

                return self.module_execution_result

            max_price_difference_percent: Union[float, int] = self.task.max_price_difference_percent
            swap_price_validation_data = await self.gecko_pricer.is_target_price_valid(
                x_token_id=coin_x_cg_id.lower(),
                y_token_id=coin_y_cg_id.lower(),
                x_amount=txn_payload_data['amount_x_decimals'],
                y_amount=txn_payload_data['amount_y_decimals'],
                max_price_difference_percent=max_price_difference_percent
            )

            is_price_valid, price_data = swap_price_validation_data
            if is_price_valid is False:
                logger.error(f"Swap rate is not valid ({module_name}). "
                             f"Gecko rate: {price_data['gecko_price']}, "
                             f"Swap rate: {price_data['target_price']}")

                return self.module_execution_result

            logger.info(f"Swap rate is valid ({module_name}). "
                        f"Gecko rate: {price_data['gecko_price']}, "
                        f"Swap rate: {price_data['target_price']}.")

        txn_status = await self.simulate_and_send_transfer_type_transaction(
            account=account,
            calls=txn_payload_data['calls'],
            txn_info_message=txn_info_message
        )

        return txn_status
