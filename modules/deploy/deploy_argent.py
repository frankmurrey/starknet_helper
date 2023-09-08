from modules.base import StarkBase
from src.schemas.configs.deploy import DeployArgentConfigSchema
from src.schemas.logs import WalletActionSchema
from src.storage import ActionStorage
from utlis.key_manager.key_manager import get_key_pair_from_pk

from starknet_py.net.account.account import Account
from starknet_py.net.models.transaction import DeployAccount
from loguru import logger


class DeployArgent(StarkBase):
    config: DeployArgentConfigSchema
    account: Account

    def __init__(self,
                 private_key: str,
                 account,
                 config):
        super().__init__(client=account.client)

        self.config = config
        self.account = account
        self.pk = private_key

    async def send_deploy_txn(self):
        key_pair = get_key_pair_from_pk(self.pk)
        class_hash = 0x025ec026985a3bf9d0cc1fe17326b245dfdc3ff89b8fde106542a3ea56c5a918
        account_initialize_call_data = [key_pair.public_key, 0]

        call_data = [
            0x33434ad846cdd5f23eb73ff09fe6fddd568284a0fb7d1be20ee482f044dabe2,
            0x79dc0da7c54b95f10aa182ad0a46400db63156920adb65eca2654c0945a463,
            len(account_initialize_call_data),
            *account_initialize_call_data
        ]

        logger.warning(f"Action: Deploy Argent account")
        current_log_action: WalletActionSchema = ActionStorage().get_current_action()
        current_log_action.module_name = self.config.module_name
        current_log_action.action_type = self.config.module_type

        account = self.get_account_argent(private_key=self.pk)
        nonce = await self.get_nonce(account=account)

        deploy_txn = DeployAccount(
            class_hash=class_hash,
            contract_address_salt=key_pair.public_key,
            constructor_calldata=call_data,
            version=1,
            max_fee=int(1e15),
            nonce=nonce,
            signature=[])

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

        logger.info(f"Gas price is under target value ({target_gas_price_gwei}), now = {gas_price / 10 ** 9} Gwei).")

        wallet_eth_balance_wei = await self.get_eth_balance(account=self.account)
        wallet_eth_balance_decimals = wallet_eth_balance_wei / 10 ** 18

        estimated_gas = await self.account._estimate_fee(tx=deploy_txn)
        overall_fee = estimated_gas.overall_fee

        if overall_fee > wallet_eth_balance_wei:
            err_msg = (f"Not enough native for fee, wallet ETH balance = {wallet_eth_balance_decimals} "
                       f"(need {overall_fee / 10 ** 18}) ")
            logger.error(err_msg)
            current_log_action.is_success = False
            current_log_action.status = err_msg
            return False

        logger.success(f"Transaction estimation success, overall fee: "
                       f"{overall_fee / 10 ** 18} ETH.")

        if self.config.test_mode is True:
            logger.debug(f"Test mode enabled. Skipping transaction")
            return False

        if self.config.forced_gas_limit is True:
            gas_limit = int(self.config.gas_limit)
        else:
            gas_limit = int(overall_fee * 1.4)

        try:
            deploy_result = await self.account.deploy_account(
                address=self.account.address,
                class_hash=class_hash,
                salt=key_pair.public_key,
                key_pair=key_pair,
                client=self.client,
                chain=self.chain_id,
                constructor_calldata=call_data,
                max_fee=gas_limit
            )

            txn_hash = deploy_result.hash

            if self.config.wait_for_receipt is True:
                logger.debug(f"Txn sent. Waiting for receipt (Timeout in {self.config.txn_wait_timeout_sec}s)."
                             f" Txn Hash: {hex(txn_hash)}")

                txn_receipt = await self.wait_for_tx_receipt(tx_hash=txn_hash,
                                                             time_out_sec=self.config.txn_wait_timeout_sec)
                if txn_receipt is False:
                    err_msg = f"Txn timeout ({self.config.txn_wait_timeout_sec}s)."
                    logger.error(err_msg)
                    current_log_action.is_success = False
                    current_log_action.status = err_msg
                    return False

                logger.success(f"Txn success, status: {txn_receipt.status} "
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
