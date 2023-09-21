import time
from datetime import datetime
from typing import Union, Optional

import aiohttp.typedefs
from loguru import logger
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId

from src.schemas import tasks
from src.schemas.wallet_data import WalletData
from src.schemas.logs import WalletActionSchema
from src.storage import Storage
from src.storage import ActionStorage
from src.action_logger import ActionLogger
from src.proxy_manager import ProxyManager
from src.custom_client_session import CustomSession

from utils.key_manager.key_manager import get_key_pair_from_pk
from utils.repr.module import print_module_config

from src import enums
import config as cfg


class ModuleExecutor:
    """
    Module executor for modules in a modules directory
    """

    def __init__(self, task: tasks.TaskBase, wallet: WalletData):
        self.task = task
        self.module_name = task.module_name
        self.module_type = task.module_type
        self.storage = Storage()
        self.action_storage = ActionStorage()

        self.app_config = self.storage.app_config

        self.wallet_data = wallet

    async def start(self) -> bool:
        print_module_config(task=self.task)
        time.sleep(cfg.DEFAULT_DELAY_SEC)

        if not self.app_config.rpc_url:
            logger.error("Please, set RPC URL in tools window or app_config.json file")
            return False

        execute_status: bool = await self.execute_module(
            wallet_data=self.wallet_data, base_url=self.app_config.rpc_url
        )

        return execute_status

    async def execute_module(
            self,
            wallet_data: WalletData,
            base_url: str
    ) -> Union[bool, None]:

        proxy_data = wallet_data.proxy
        proxy_manager = ProxyManager(proxy_data=proxy_data)
        proxies = proxy_manager.get_proxy()

        if self.task.test_mode is False:
            self.action_storage.create_and_set_new_logs_dir()

        action_log_data = WalletActionSchema(
            date_time=datetime.now().strftime("%d-%m-%Y_%H-%M-%S"),
            wallet_address=wallet_data.address,
        )

        if proxy_data:
            proxy_body = f"{proxy_data.host}:{proxy_data.port}"
            action_log_data.proxy = proxy_body

            proxy_set_up_status = False

            if (
                proxy_data.is_mobile is True
                and self.app_config.mobile_proxy_rotation is True
            ):
                rotation_link = self.app_config.mobile_proxy_rotation_link
                if not rotation_link:
                    err_msg = (
                        "Mobile proxy rotation link is not set (go to app_config.json)"
                    )
                    logger.error(err_msg)

                    action_log_data.is_success = False
                    action_log_data.status = err_msg

                rotate_status = proxy_manager.rotate_mobile_proxy(rotation_link)
                if rotate_status is False:
                    err_msg = "Mobile proxy rotation failed"
                    logger.error(err_msg)

                    action_log_data.is_success = False
                    action_log_data.status = err_msg

            current_ip = proxy_manager.get_ip()
            if current_ip is None:
                err_msg = f"Proxy {wallet_data.proxy.host}:{wallet_data.proxy.port} is not valid or bad auth params"
                logger.error(err_msg)

                action_log_data.is_success = False
                action_log_data.status = err_msg

            else:
                proxy_set_up_status = True

                logger.info(
                    f"Proxy valid, using {wallet_data.proxy.host}:{wallet_data.proxy.port} (ip: {current_ip})"
                )

            if proxy_set_up_status is False:
                action_logger = ActionLogger(action_data=action_log_data)
                action_logger.log_error()
                return False

        self.action_storage.update_current_action(action_data=action_log_data)
        key_pair = get_key_pair_from_pk(wallet_data.private_key)

        proxy_unit: Optional[aiohttp.typedefs.StrOrURL] = (
            proxies.get("http://") if proxies else None
        )

        connector = aiohttp.TCPConnector(limit=10)
        custom_session = CustomSession(proxy=proxy_unit, connector=connector)
        client = FullNodeClient(node_url=base_url, session=custom_session)

        account = Account(
            address=wallet_data.address,
            client=client,
            key_pair=key_pair,
            chain=StarknetChainId.MAINNET,
        )

        if self.module_name == enums.ModuleName.DEPLOY:
            assert isinstance(self.task, tasks.DeployTask)

            module = self.task.module(
                private_key=wallet_data.private_key,
                account=account,
                task=self.task,
                key_type=wallet_data.type,
            )
            execution_status = await module.send_txn()

        elif self.module_name == enums.ModuleName.TRANSFER:
            module = self.task.module(
                account=account,
                task=self.task,
                wallet_data=wallet_data
            )

            execution_status = await module.send_txn()

        else:
            module = self.task.module(account=account, task=self.task)
            execution_status = await module.send_txn()

        if self.task.test_mode is False:
            ActionLogger.log_action_from_storage()

        await connector.close()

        return execution_status
