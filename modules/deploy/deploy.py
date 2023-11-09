from typing import TYPE_CHECKING, Union

from loguru import logger
from starknet_py.net.account.account import Account
from starknet_py.net.client_errors import ClientError
from starknet_py.net.models.transaction import DeployAccount

from src import enums
from modules.base import ModuleBase
from modules.deploy.custom_curve_signer import BraavosCurveSigner
from src.schemas.action_models import ModuleExecutionResult
from utils.key_manager.key_manager import get_key_pair_from_pk, get_key_data

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
            account=account,
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

    async def send_txn(self) -> ModuleExecutionResult:
        """
        Send deploy transaction
        :return:
        """
        account_deployed = await self.account_deployed(account=self.account)
        if account_deployed is True:
            err_msg = f"Account already deployed."
            logger.warning(err_msg)
            self.module_execution_result.execution_info = err_msg
            self.module_execution_result.retry_needed = False
            return self.module_execution_result

        logger.warning(f"Action: Deploy {self.key_type.title()} account")

        signed_deploy_txn = await self.build_deploy_txn()
        if signed_deploy_txn is None:
            err_msg = f"Error while estimating transaction fee"
            logger.error(err_msg)
            self.module_execution_result.execution_info = err_msg

        wallet_eth_balance_wei = await self.get_eth_balance(account=self.account)
        wallet_eth_balance_decimals = wallet_eth_balance_wei / 10 ** 18

        try:
            estimated_fee = await self.account.client.estimate_fee(tx=signed_deploy_txn)
            overall_fee = estimated_fee.overall_fee

        except ClientError:
            err_msg = f"Error while estimating transaction fee"
            logger.error(err_msg)

            self.module_execution_result.execution_info = err_msg
            return self.module_execution_result

        overall_fee = int(overall_fee * 2)
        if overall_fee is None:
            err_msg = f"Error while estimating transaction fee."
            logger.error(err_msg)

            self.module_execution_result.execution_info = err_msg
            return self.module_execution_result

        if overall_fee > wallet_eth_balance_wei:
            err_msg = (f"Not enough native for fee, wallet ETH balance = {wallet_eth_balance_decimals} "
                       f"(need {overall_fee / 10 ** 18}) ")
            logger.error(err_msg)

            self.module_execution_result.execution_info = err_msg
            return self.module_execution_result

        logger.success(f"Transaction estimation success, overall fee: "
                       f"{overall_fee / 10 ** 18} ETH.")

        if self.task.test_mode is True:
            err_msg = f"Test mode enabled. Skipping transaction"

            self.module_execution_result.execution_info = err_msg
            return self.module_execution_result

        try:
            deploy_result = await self.account.client.deploy_account(signed_deploy_txn)
            txn_hash = deploy_result.transaction_hash

            if self.task.wait_for_receipt is True:
                logger.info(f"Txn sent. Waiting for receipt (Timeout in {self.task.txn_wait_timeout_sec}s)."
                            f" Txn Hash: {hex(txn_hash)}")

                txn_receipt = await self.wait_for_tx_receipt(tx_hash=txn_hash,
                                                             time_out_sec=int(self.task.txn_wait_timeout_sec))
                if txn_receipt is None:
                    err_msg = f"Txn timeout ({self.task.txn_wait_timeout_sec}s)."
                    logger.error(err_msg)

                    self.module_execution_result.execution_info = err_msg
                    return self.module_execution_result

                txn_status = txn_receipt.execution_status.value if txn_receipt.execution_status is not None else None
                logger.success(f"Txn success, status: {txn_status} "
                               f"(Actual fee: {txn_receipt.actual_fee / 10 ** 18}). "
                               f"Txn Hash: {hex(txn_hash)})")

                self.module_execution_result.execution_status = True
                self.module_execution_result.execution_info = f"Txn success, status: {txn_status}"
                self.module_execution_result.hash = hex(txn_hash)

                return self.module_execution_result

            else:
                logger.success(f"Txn sent. Txn Hash: {hex(txn_hash)}")

                self.module_execution_result.execution_status = True
                self.module_execution_result.execution_info = f"Txn sent"
                self.module_execution_result.hash = hex(txn_hash)
                return self.module_execution_result

        except Exception as e:
            err_msg = f"Error while sending deploy txn: {e}"
            logger.error(err_msg)

            self.module_execution_result.execution_info = err_msg
            return self.module_execution_result
