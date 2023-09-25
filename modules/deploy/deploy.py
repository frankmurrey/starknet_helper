import dataclasses
from typing import TYPE_CHECKING, Union

from starknet_py.net.account.account import Account
from starknet_py.net.models.transaction import DeployAccount
from starknet_py.net.client_errors import ClientError
from loguru import logger

from modules.base import ModuleBase
from src.schemas.logs import WalletActionSchema
from src import enums
from src.storage import ActionStorage
from utils.key_manager.key_manager import get_key_pair_from_pk, get_key_data
from modules.deploy.custom_curve_signer import BraavosCurveSigner

if TYPE_CHECKING:
    from src.schemas.tasks.deploy import DeployTask


class Deploy(ModuleBase):
    task: 'DeployTask'
    account: Account

    def __init__(
            self,
            private_key: str,
            key_type: enums.PrivateKeyType,
            account,
            task: 'DeployTask',
    ):
        super().__init__(
            client=account.client,
            task=task
        )

        self.task = task
        self.account = account
        self.pk = private_key

        self.key_type = key_type
        self.key_pair = get_key_pair_from_pk(self.pk)
        self.key_data = get_key_data(key_pair=self.key_pair, key_type=self.key_type)

        if self.key_type == enums.PrivateKeyType.braavos:
            self.account.signer = BraavosCurveSigner(
                account_address=self.account.address,
                key_pair=self.key_pair,
                chain_id=self.chain_id
            )

    async def build_deploy_txn(self) -> Union[DeployAccount, None]:
        """
        Build signed deploy account transaction
        :return:
        """
        nonce = await self.get_nonce(account=self.account)

        max_fee = None
        estimated_fee = True

        if self.task.forced_gas_limit:
            max_fee = int(self.task.max_fee * 10 ** 9)
            estimated_fee = None

        try:
            deploy_account_tx = await self.account.sign_deploy_account_transaction(
                class_hash=self.key_data.class_hash,
                contract_address_salt=self.key_pair.public_key,
                constructor_calldata=self.key_data.call_data,
                nonce=nonce,
                max_fee=max_fee,
                auto_estimate=estimated_fee
            )

            return deploy_account_tx

        except ClientError as e:
            if "unavailable for deployment" in str(e):
                err_msg = f"Account unavailable for deployment or already deployed."
                logger.error(err_msg)
                return None

            else:
                err_msg = f"Error while estimating transaction fee"
                logger.error(err_msg)
                return None

    async def send_txn(self):
        """
        Send deploy transaction
        :return:
        """
        account_deployed = await self.account_deployed(account=self.account)
        if account_deployed is True:
            logger.warning(f"Account already deployed.")
            return False

        logger.warning(f"Action: Deploy {self.key_type.title()} account")
        current_log_action: WalletActionSchema = ActionStorage().get_current_action()
        current_log_action.module_name = self.task.module_name
        current_log_action.action_type = self.task.module_type

        signed_deploy_txn = await self.build_deploy_txn()
        if signed_deploy_txn is None:
            err_msg = f"Error while estimating transaction fee"
            logger.error(err_msg)
            current_log_action.is_success = False
            current_log_action.status = err_msg
            return False

        target_gas_price_gwei = self.storage.app_config.target_eth_mainnet_gas_price
        target_gas_price_wei = target_gas_price_gwei * 10 ** 9
        time_out_sec = self.storage.app_config.time_to_wait_target_gas_price_sec
        gas_price_status = await self.gas_price_check_loop(target_price_wei=target_gas_price_wei,
                                                           time_out_sec=time_out_sec)
        status, gas_price = gas_price_status
        if status is False:
            err_msg = f"Gas price is too high ({gas_price / 10 ** 9} Gwei) after {time_out_sec}. Aborting transaction."
            logger.error(err_msg)

            current_log_action.is_success = False
            current_log_action.status = err_msg
            return False

        logger.info(f"Gas price is under target value ({target_gas_price_gwei}), now = {gas_price / 10 ** 9} Gwei.")

        wallet_eth_balance_wei = await self.get_eth_balance(account=self.account)
        wallet_eth_balance_decimals = wallet_eth_balance_wei / 10 ** 18

        try:
            estimated_fee = await self.account.client.estimate_fee(tx=signed_deploy_txn)
            overall_fee = estimated_fee.overall_fee

        except ClientError:
            err_msg = f"Error while estimating transaction fee"
            logger.error(err_msg)
            current_log_action.is_success = False
            current_log_action.status = err_msg
            return False

        overall_fee = int(overall_fee * 2)
        if overall_fee is None:
            err_msg = f"Error while estimating transaction fee."
            logger.error(err_msg)
            current_log_action.is_success = False
            current_log_action.status = err_msg
            return False

        if overall_fee > wallet_eth_balance_wei:
            err_msg = (f"Not enough native for fee, wallet ETH balance = {wallet_eth_balance_decimals} "
                       f"(need {overall_fee / 10 ** 18}) ")
            logger.error(err_msg)
            current_log_action.is_success = False
            current_log_action.status = err_msg
            return False

        logger.success(f"Transaction estimation success, overall fee: "
                       f"{overall_fee / 10 ** 18} ETH.")

        if self.task.test_mode is True:
            logger.info(f"Test mode enabled. Skipping transaction")
            return False

        try:
            deploy_result = await self.account.client.deploy_account(signed_deploy_txn)
            txn_hash = deploy_result.transaction_hash

            if self.task.wait_for_receipt is True:
                logger.info(f"Txn sent. Waiting for receipt (Timeout in {self.task.txn_wait_timeout_sec}s)."
                            f" Txn Hash: {hex(txn_hash)}")

                txn_receipt = await self.wait_for_tx_receipt(tx_hash=txn_hash,
                                                             time_out_sec=int(self.task.txn_wait_timeout_sec))
                if txn_receipt is False:
                    err_msg = f"Txn timeout ({self.task.txn_wait_timeout_sec}s)."
                    logger.error(err_msg)
                    current_log_action.is_success = False
                    current_log_action.status = err_msg
                    return False

                logger.success(f"Txn success, status: {txn_receipt.execution_status} "
                               f"(Actual fee: {txn_receipt.actual_fee / 10 ** 18}. "
                               f"Txn Hash: {hex(txn_hash)})")

                current_log_action.is_success = True
                current_log_action.status = f"Txn success, status: {txn_receipt.status}"
                current_log_action.transaction_hash = hex(txn_hash)
                return True

            else:
                logger.success(f"Txn sent. Txn Hash: {hex(txn_hash)}")
                current_log_action.is_success = True
                current_log_action.status = "Txn sent"
                current_log_action.transaction_hash = hex(txn_hash)
                return True

        except Exception as e:
            err_msg = f"Error while sending deploy txn: {e}"
            logger.error(err_msg)
            current_log_action.is_success = False
            current_log_action.status = err_msg
            return False
