import random
import time
from typing import Union
from typing import TYPE_CHECKING
from typing import Callable

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
from src.schemas.action_models import ModuleExecutionResult, TransactionPayloadData
from src.gecko_pricer import GeckoPricer
from src.storage import Storage
from src.execution_storage import ExecutionStorage
from src import paths
from src import enums
from utils.file_manager import FileManager
from utils.misc import decode_wallet_version
from contracts.tokens.main import Tokens
from contracts.base import TokenBase
import config

if TYPE_CHECKING:
    from src.schemas.tasks.base.swap import SwapTaskBase
    from src.schemas.tasks.base.add_liquidity import AddLiquidityTaskBase
    from src.schemas.tasks.base.remove_liquidity import RemoveLiquidityTaskBase
    from src.schemas.tasks.base import TaskBase
    from src.schemas.wallet_data import WalletData


class ModuleBase:
    ETH_ADDRESS_MAINNET = '0x049D36570D4E46F48E99674BD3FCC84644DDD6B96F7C741B1562B82F9E004DC7'

    def __init__(
            self,
            account: Account,
            task: 'TaskBase',
            wallet_data: 'WalletData'
    ):
        self.account = account
        self.client = account.client
        self.chain_id = StarknetChainId.MAINNET
        self.gecko_pricer = GeckoPricer(client=self.client)
        self.storage = Storage()
        self.tokens = Tokens()
        self.is_task_virtual = getattr(task, 'is_virtual', False)

        self.task = task
        self.wallet_data = wallet_data

        self.execution_storage = ExecutionStorage()

        self.module_execution_result = ModuleExecutionResult(test_mode=self.task.test_mode)

    def i16(
            self,
            hex_d: str
    ):
        return int(hex_d, 16)

    def log_error(self, msg: str):
        logger.error(msg)
        self.module_execution_result.execution_status = False
        self.module_execution_result.execution_info += msg + "\n"

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
            address: Union[str, int],
            abi: list,
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
            res = await token_contract.functions['decimals'].call()
            res_dict = res.as_dict()

            decimals = res_dict.get('decimals')
            if decimals is None:

                decimals = res_dict.get('res')
                if decimals is None:
                    return None

            return decimals

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
            token_address: Union[str, int]
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

        except ClientError as ex:
            logger.error(f"Error while signing transaction: {ex}")
            return None

    async def build_txn_payload_data(self) -> TransactionPayloadData:
        """
        ABC method for building transaction payload data. Must be implemented in child classes.
        :return:
        """
        raise NotImplementedError

    async def build_reverse_txn_payload_data(self) -> TransactionPayloadData:
        """
        ABC method for building reverse transaction payload data. Must be implemented in child classes.
        :return:
        """
        raise NotImplementedError

    async def send_txn(self) -> ModuleExecutionResult:
        """
        ABC method for sending a transaction. Must be implemented in child classes.
        :return:
        """

    async def try_send_txn(
            self,
            retries: int = 1,
    ) -> ModuleExecutionResult:
        """
        Tries to send a transaction. Retries if needed.
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

        cairo_version = await self.get_cairo_version_for_txn_execution(account=account)
        if cairo_version is None:
            self.log_error("Error while getting Cairo version")
            return self.module_execution_result

        signed_invoke_transaction = await self.sign_invoke_transaction(
            account=account,
            calls=calls,
            cairo_version=cairo_version,
            auto_estimate=not self.task.forced_gas_limit
        )
        if signed_invoke_transaction is None:
            self.log_error("Error while signing transaction (Usually caused by incorrect payload data)")
            return self.module_execution_result

        time.sleep(1)
        estimate_transaction = await self.get_estimated_transaction_fee(
            account=account,
            transaction=signed_invoke_transaction
        )
        if estimate_transaction is None:
            self.log_error("Transaction estimation failed")
            return self.module_execution_result

        estimate_gas_decimals = estimate_transaction / 10 ** 18
        wallet_eth_balance = await self.get_eth_balance(account=account)
        if wallet_eth_balance is None:
            self.log_error("Error while getting wallet ETH balance")
            return self.module_execution_result

        wallet_eth_balance_decimals = wallet_eth_balance / 10 ** 18

        if wallet_eth_balance < estimate_transaction:
            err_msg = (
                f"Insufficient ETH balance for txn fees (balance: {wallet_eth_balance_decimals}, "
                f"need {estimate_gas_decimals} ETH)"
            )
            self.log_error(err_msg)
            return self.module_execution_result

        estimate_msg = f"Transaction estimation success, overall fee: {estimate_gas_decimals} ETH."
        logger.success(estimate_msg)

        max_fee = int(self.task.max_fee) * 10 ** 9 if self.task.forced_gas_limit is True else None

        if self.task.test_mode is True:
            self.module_execution_result.execution_info += estimate_msg
            self.module_execution_result.execution_status = True
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
            self.log_error(f"Error while sending txn, {response}")
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
                self.log_error(f"Transaction failed or not in blockchain after {self.task.txn_wait_timeout_sec}s")
                self.module_execution_result.hash = hex(txn_hash)
                return self.module_execution_result

            txn_status = txn_receipt.execution_status.value if txn_receipt.execution_status is not None else None

            logger.success(
                f"Txn success, status: {txn_status} "
                f"(Actual fee: {txn_receipt.actual_fee / 10 ** 18}). "
                f"Txn Hash: {hex(txn_hash)})"
            )

            self.module_execution_result.execution_status = True
            self.module_execution_result.execution_info += f"Txn success, status: {txn_status}," \
                                                           f" fee: {txn_receipt.actual_fee / 10 ** 18} ETH"
            self.module_execution_result.hash = hex(txn_hash)
            return self.module_execution_result

        else:
            logger.success(f"Txn sent. Txn Hash: {hex(txn_hash)}")

            self.module_execution_result.execution_status = True
            self.module_execution_result.execution_info += "Txn sent (Receipt not requested)"
            self.module_execution_result.hash = hex(txn_hash)

            return self.module_execution_result


class SwapModuleBase(ModuleBase):
    task: 'SwapTaskBase'

    def __init__(
            self,
            account,
            task: 'SwapTaskBase',
            wallet_data: 'WalletData'
    ):
        super().__init__(account=account, task=task, wallet_data=wallet_data)
        self.account: Account = account

        if not self.task.coin_y == enums.MiscTypes.RANDOM:

            if not self.is_task_virtual:

                self.coin_x = self.tokens.get_by_name(self.task.coin_x)
                self.coin_y = self.tokens.get_by_name(self.task.coin_y)

                self.initial_balance_x_wei = None
                self.initial_balance_y_wei = None

                self.build_payload_data: Callable = self.build_txn_payload_data

            else:
                self.coin_x = self.tokens.get_by_name(self.task.coin_y)
                self.coin_y = self.tokens.get_by_name(self.task.coin_x)

                self.initial_balance_x_wei = self.execution_storage.get_by_wallet_id_and_task_id(
                    wallet_id=self.wallet_data.wallet_id,
                    task_id=self.task.task_id
                ).get('initial_balance_y_wei')
                self.initial_balance_y_wei = self.execution_storage.get_by_wallet_id_and_task_id(
                    wallet_id=self.wallet_data.wallet_id,
                    task_id=self.task.task_id
                ).get('initial_balance_x_wei')

                self.build_payload_data: Callable = self.build_reverse_txn_payload_data

            self.token_x_decimals = None
            self.token_y_decimals = None

    async def set_fetched_tokens_data(self):
        """
        Fetches initial balances and token decimals for both tokens.
        :return:
        """
        self.initial_balance_x_wei = await self.get_token_balance(
            token_address=self.coin_x.contract_address,
            account=self.account
        )
        self.initial_balance_y_wei = await self.get_token_balance(
            token_address=self.coin_y.contract_address,
            account=self.account
        )

        self.execution_storage.set_pre_execution_data(
            wallet_id=self.wallet_data.wallet_id,
            task_id=self.task.task_id,
            data={
                'initial_balance_x_wei': self.initial_balance_x_wei,
                'initial_balance_y_wei': self.initial_balance_y_wei
            },
        )

        self.token_x_decimals = await self.get_token_decimals(
            contract_address=self.coin_x.contract_address,
            abi=self.coin_x.abi,
            provider=self.account
        )
        self.token_y_decimals = await self.get_token_decimals(
            contract_address=self.coin_y.contract_address,
            abi=self.coin_y.abi,
            provider=self.account
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
            self.log_error(f"Wallet {coin_x.symbol.upper()} balance = 0")
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
            self.log_error(
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

    async def send_txn(self) -> ModuleExecutionResult:
        """
        Sends a swap transaction. Reimplemented from parent 'ModuleBase' class.
        :return:
        """

        await self.set_fetched_tokens_data()

        if self.check_local_tokens_data() is False:
            self.module_execution_result.execution_info += f"Failed to fetch local tokens data in swap module"
            return self.module_execution_result

        txn_payload_data = await self.build_payload_data()
        if txn_payload_data is None:
            self.module_execution_result.execution_info += f"Failed to build transaction payload data"
            return self.module_execution_result

        self.task: 'SwapTaskBase'

        module_name = self.task.module_name.title()

        out_decimals = txn_payload_data.amount_x_decimals
        in_decimals = txn_payload_data.amount_y_decimals

        coin_x_symbol = self.task.coin_x.upper()
        coin_y_symbol = self.task.coin_y.upper()

        slippage: Union[float, int] = self.task.slippage

        is_reverse_label = f"Reverse " if self.is_task_virtual else ""

        txn_info_message = f"{is_reverse_label}Swap ({module_name}) | " \
                           f"{out_decimals} ({coin_x_symbol}) -> " \
                           f"{in_decimals} ({coin_y_symbol}). " \
                           f"Slippage: {slippage}%."

        if self.task.compare_with_cg_price is True:
            coin_x_cg_id = self.tokens.get_cg_id_by_name(coin_x_symbol)
            coin_y_cg_id = self.tokens.get_cg_id_by_name(coin_y_symbol)
            if coin_x_cg_id is None or coin_y_cg_id is None:
                self.log_error(f"Error while getting CoinGecko IDs for {coin_x_symbol.upper()} and {coin_y_symbol.upper()}")
                return self.module_execution_result

            max_price_difference_percent: Union[float, int] = self.task.max_price_difference_percent
            swap_price_validation_data = await self.gecko_pricer.is_target_price_valid(
                x_token_id=coin_x_cg_id.lower(),
                y_token_id=coin_y_cg_id.lower(),
                x_amount=txn_payload_data.amount_x_decimals,
                y_amount=txn_payload_data.amount_y_decimals,
                max_price_difference_percent=max_price_difference_percent
            )

            is_price_valid, price_data = swap_price_validation_data
            if is_price_valid is False:
                err_msg = f"Swap rate is not valid ({module_name}). " \
                            f"Gecko rate: {price_data['gecko_price']}, " \
                            f"Swap rate: {price_data['target_price']}"
                self.log_error(err_msg)
                return self.module_execution_result

            logger.info(f"Swap rate is valid ({module_name}). "
                        f"Gecko rate: {price_data['gecko_price']}, "
                        f"Swap rate: {price_data['target_price']}.")

        txn_status = await self.simulate_and_send_transfer_type_transaction(
            account=self.account,
            calls=txn_payload_data.calls,
            txn_info_message=txn_info_message
        )

        return txn_status


class LiquidityModuleBase(ModuleBase):
    task: Union['AddLiquidityTaskBase', 'RemoveLiquidityTaskBase']

    def __init__(
            self,
            account,
            wallet_data: 'WalletData',
            task: Union['AddLiquidityTaskBase', 'RemoveLiquidityTaskBase']
    ):
        super().__init__(account=account, task=task, wallet_data=wallet_data)
        self._account = account

        if not self.task.coin_y == enums.MiscTypes.RANDOM:

            self.coin_x = self.tokens.get_by_name(self.task.coin_x)
            self.coin_y = self.tokens.get_by_name(self.task.coin_y)

            if not self.is_task_virtual:

                self.initial_balance_x_wei = None
                self.initial_balance_y_wei = None

                self.build_payload_data: Callable = self.build_txn_payload_data

            else:

                self.reverse_task = self.task.reverse_action_task
                self.reverse_task: 'RemoveLiquidityTaskBase'

                self.reverse_module = self.reverse_task.module
                self.reverse_module: 'LiquidityModuleBase'

                self.build_payload_data: Callable = self.reverse_module.build_txn_payload_data

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
            self.log_error(
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

    async def send_txn(self) -> ModuleExecutionResult:
        """
        Sends a liquidity transaction. Reimplemented from parent 'ModuleBase' class.
        :return:
        """

        await self.set_fetched_tokens_data()

        if self.check_local_tokens_data() is False:
            self.log_error(f"Failed to fetch local tokens data in swap module")
            return self.module_execution_result

        txn_payload_data = await self.build_payload_data()
        if txn_payload_data is None:
            self.log_error(f"Failed to build transaction payload data")
            return self.module_execution_result

        module_name = self.task.module_name.title()
        module_type = "Add liquidity" if not self.is_task_virtual else "Remove liquidity"

        out_decimals = txn_payload_data.amount_x_decimals
        in_decimals = txn_payload_data.amount_y_decimals

        coin_x_symbol = self.coin_x.symbol.upper()
        coin_y_symbol = self.coin_y.symbol.upper()

        txn_info_message = f"{module_type} ({module_name}) | " \
                           f"{out_decimals} ({coin_x_symbol.upper()}) + " \
                           f"{in_decimals} ({coin_y_symbol.upper()}). " \
                           f"Slippage: {self.task.slippage}%."

        txn_status = await self.simulate_and_send_transfer_type_transaction(
            account=self.account,
            calls=txn_payload_data.calls,
            txn_info_message=txn_info_message
        )

        return txn_status
