from typing import TYPE_CHECKING

from starknet_py.net.account.account import Account
from starknet_py.net.client_errors import ClientError
from loguru import logger

import config
from modules.base import ModuleBase
from src.schemas.logs import WalletActionSchema
from src import enums
from src import paths
from src.storage import ActionStorage
from src.storage import Storage
from utlis.file_manager import FileManager
from utlis.key_manager.key_manager import get_key_pair_from_pk

if TYPE_CHECKING:
    from src.schemas.tasks.deploy import UpgradeTask


class Upgrade(ModuleBase):
    task: 'UpgradeTask'
    account: Account

    def __init__(
            self,
            account,
            task: 'UpgradeTask',
    ):
        super().__init__(
            client=account.client,
            task=task
        )

        self.task = task
        self.account = account

    async def upgrade_needed(
            self,
            account_contract) -> bool:
        try:
            version = await account_contract.functions['getVersion'].call()

            version_decoded = self.decode_version(version=version.version)
            last_provided_version = Storage().app_config.last_wallet_version

            if version_decoded == last_provided_version:
                logger.info(f'Account does not need upgrade, version: {version_decoded}')
                return False

            logger.info(f'Account needs upgrade,'
                        f' account version: {version_decoded},'
                        f' last version: {last_provided_version}')
            return True

        except ClientError:
            logger.error(f'Error while getting account contract or wallet not deployed')
            return False

    async def build_txn_payload_calls(self):
        account_contract = await self.get_account_contract(
            address=self.account.address,
            abi=FileManager.read_abi_from_file(paths.ACCOUNT_ABI_FILE),
            provider=self.account,
        )

        upgrade_needed = await self.upgrade_needed(account_contract=account_contract)
        if not upgrade_needed:
            return None

        upgrade_call = account_contract.functions['upgrade'].prepare(
            implementation=config.IMPLEMENTATION_ADDRESS,
            calldata=[0]
        )

        calls = [upgrade_call]

        return calls

    async def send_txn(self):
        txn_payload_calls = await self.build_txn_payload_calls()
        if txn_payload_calls is None:
            return False

        txn_info_message = f"Wallet version upgrade"

        txn_status = await self.simulate_and_send_transfer_type_transaction(
            account=self.account,
            calls=txn_payload_calls,
            txn_info_message=txn_info_message,
        )

        return txn_status
