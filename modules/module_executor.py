import time
import random
from datetime import timedelta, datetime
from typing import List, Union, Callable

from loguru import logger
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId

from modules.myswap.swap import MySwap
from src.schemas.configs.base import CommonSettingsBase
from src.schemas.configs.app_config import AppConfigSchema
from src.schemas.wallet_data import WalletData
from src.storage import Storage
from src.proxy_manager import ProxyManager

from modules.jediswap.swap import JediSwap
from modules.deploy.deploy_argent import DeployArgent

from utlis.key_manager.key_manager import get_argent_addr_from_private_key
from utlis.key_manager.key_manager import get_braavos_addr_from_private_key
from utlis.key_manager.key_manager import get_key_pair_from_pk
from utlis.xlsx import write_balance_data_to_xlsx

from src import enums
import config as cfg


class ModuleExecutor:
    """
    Module executor for modules in a modules directory
    """

    def __init__(self, config: CommonSettingsBase):
        self.config = config
        self.module_name = config.module_name
        self.storage = Storage()

        self.app_config = AppConfigSchema()  # TODO: Get from storage

        self.wallets: List[WalletData] = []

        if self.app_config.private_key_type == enums.PrivateKeyType.braavos:
            self.get_addr_from_private_key: Callable[[str], str] = get_braavos_addr_from_private_key
        elif self.app_config.private_key_type == enums.PrivateKeyType.argent:
            self.get_addr_from_private_key: Callable[[str], str] = get_argent_addr_from_private_key
        else:
            raise ValueError(f"Invalid private key type: {self.app_config.private_key_type}")

    def get_delay_sec(self, execution_status: bool) -> int:
        """
        Get the delay in seconds based on the execution status.

        Args:
            execution_status (bool): The execution status of the function.

        Returns:
            int: The delay in seconds.

        """
        if execution_status is True:
            return random.randint(self.config.min_delay_sec, self.config.max_delay_sec)

        return cfg.DEFAULT_DELAY_SEC

    def blur_private_key(self, private_key: str) -> str:
        """
        This function takes a private key as input and blurs it by replacing a portion of the key with asterisks.

        Parameters:
        - private_key (str): The private key that needs to be blurred.

        Returns:
        - blurred_private_key (str): The blurred version of the private key.
        """
        length = len(private_key)
        start_index = length // 10
        end_index = length - start_index
        blurred_private_key = private_key[:start_index] + '*' * (end_index - start_index) + private_key[end_index + 4:]

        return blurred_private_key

    async def start(self):
        # TODO: Print config

        if not self.app_config.rpc_url:
            logger.error("Please, set RPC URL in tools window or app_config.json file")
            return

        if self.app_config.shuffle_wallets:
            random.shuffle(self.wallets)

        wallets_amount = len(self.wallets)
        for index, wallet_data in enumerate(self.wallets):
            wallet_address = self.get_addr_from_private_key(wallet_data.private_key)

            logger.info(f"[{index + 1}] - {hex(wallet_address)}")
            logger.info(f"PK - {self.blur_private_key(wallet_data.private_key)}")

            execute_status: bool = await self.execute_module(wallet_data=wallet_data,
                                                             base_url=self.app_config.rpc_url)

            if index == wallets_amount - 1:
                logger.info(f"Process is finished\n")
                break

            time_delay_sec = self.get_delay_sec(execution_status=execute_status)

            delta = timedelta(seconds=time_delay_sec)
            result_datetime = datetime.now() + delta

            logger.info(f"Waiting {time_delay_sec} seconds, next wallet {result_datetime}\n")
            time.sleep(time_delay_sec)

    async def execute_module(self,
                             wallet_data: WalletData,
                             base_url: str) -> Union[bool, None]:

        execution_status = None

        proxy_data = wallet_data.proxy
        proxy_manager = ProxyManager(proxy_data=proxy_data)
        proxies = proxy_manager.get_proxy()

        if proxy_data:
            proxy_body = f"{proxy_data.host}:{proxy_data.port}"
            if proxy_data.is_mobile is True and self.app_config.mobile_proxy_rotation is True:
                rotation_link = self.app_config.mobile_proxy_rotation_link
                if not rotation_link:
                    err_msg = "Mobile proxy rotation link is not set (go to app_config.json)"
                    logger.error(err_msg)

                    # TODO: Log all actions to xlsx

                    return False

                rotate_status = proxy_manager.rotate_mobile_proxy(rotation_link)
                if rotate_status is False:
                    err_msg = "Mobile proxy rotation failed"

                    # TODO: Log all actions to xlsx

                    return False

            current_ip = proxy_manager.get_ip()
            if current_ip is None:
                err_msg = f"Proxy {wallet_data.proxy.host}:{wallet_data.proxy.port} is not valid or bad auth params"
                logger.error(err_msg)

                # TODO: Log all actions to xlsx

                return False
            else:
                logger.info(
                    f"Proxy valid, using {wallet_data.proxy.host}:{wallet_data.proxy.port} (ip: {current_ip})")

        wallet_address = self.get_addr_from_private_key(wallet_data.private_key)
        key_pair = get_key_pair_from_pk(wallet_data.private_key)
        client = FullNodeClient(node_url=base_url)
        account = Account(
            address=wallet_address,
            client=client,
            key_pair=key_pair,
            chain=StarknetChainId.MAINNET
        )

        if self.module_name == enums.ModuleName.JEDI_SWAP:
            module = JediSwap(
                account=account,
                config=self.config
            )
            execution_status = await module.send_swap_txn()

        elif self.module_name == enums.ModuleName.MY_SWAP:
            pass

        elif self.module_name == enums.ModuleName.DEPLOY_ARGENT:
            module = DeployArgent(
                account=account,
                config=self.config,
                private_key=wallet_data.private_key
            )
            execution_status = await module.send_deploy_txn()

        else:
            raise ValueError(f"Invalid module name: {self.module_name}")

        return execution_status
