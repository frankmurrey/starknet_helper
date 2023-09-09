import time
import random
from datetime import timedelta, datetime
from typing import List, Union, Callable, Optional

import aiohttp.typedefs
from loguru import logger
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId

from src.schemas.configs.base import CommonSettingsBase
from src.schemas.configs.app_config import AppConfigSchema
from src.schemas.wallet_data import WalletData
from src.schemas.logs import WalletActionSchema
from src.storage import Storage
from src.storage import ActionStorage
from src.action_logger import ActionLogger
from src.proxy_manager import ProxyManager
from src.custom_client_session import CustomSession

from modules.jediswap.swap import JediSwap
from modules.jediswap.liquidity import JediSwapAddLiquidity
from modules.jediswap.liquidity import JediSwapRemoveLiquidity
from modules.myswap.swap import MySwap
from modules.myswap.liquidity import MySwapAddLiquidity
from modules.myswap.liquidity import MySwapRemoveLiquidity
from modules.deploy.deploy_argent import DeployArgent
from modules.deploy.deploy_braavos import DeployBraavos
from modules.avnu.swap import AvnuSwap
from modules.sithswap.swap import SithSwap
from modules.sithswap.liquidity import SithSwapAddLiquidity
from modules.sithswap.liquidity import SithSwapRemoveLiquidity
from modules.k10swap.swap import K10Swap
from modules.starknet_id.identity_mint import IdentityMint
from modules.zklend.supply import ZkLendSupply
from modules.zklend.withdraw import ZkLendWithdraw
from modules.test import ModulesTest


from utlis.key_manager.key_manager import get_argent_addr_from_private_key
from utlis.key_manager.key_manager import get_braavos_addr_from_private_key
from utlis.key_manager.key_manager import get_key_pair_from_pk
from utlis.xlsx import write_balance_data_to_xlsx
from utlis.repr.module import print_module_config

from src import enums
import config as cfg


class ModuleExecutor:
    """
    Module executor for modules in a modules directory
    """

    def __init__(self, config: CommonSettingsBase):
        self.config = config
        self.module_name = config.module_name
        self.module_type = config.module_type
        self.storage = Storage()
        self.action_storage = ActionStorage()

        self.app_config = self.storage.app_config

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
        print_module_config(module_config=self.config)
        time.sleep(cfg.DEFAULT_DELAY_SEC)

        if not self.app_config.rpc_url:
            logger.error("Please, set RPC URL in tools window or app_config.json file")
            return

        wallets = self.wallets.copy()
        if self.app_config.shuffle_wallets:
            random.shuffle(wallets)

        if self.config.test_mode:
            wallets = wallets[:3]
            logger.warning(f"Test mode enabled. Working only with {len(wallets)} wallets\n")

        wallets_amount = len(wallets)
        for index, wallet_data in enumerate(wallets):
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
        wallet_address: int = self.get_addr_from_private_key(wallet_data.private_key)

        proxy_data = wallet_data.proxy
        proxy_manager = ProxyManager(proxy_data=proxy_data)
        proxies = proxy_manager.get_proxy()

        if self.config.test_mode is False:
            self.action_storage.create_and_set_new_logs_dir()

        action_log_data = WalletActionSchema(
            date_time=datetime.now().strftime("%d-%m-%Y_%H-%M-%S"),
            wallet_address=hex(wallet_address)
        )

        if proxy_data:
            proxy_body = f"{proxy_data.host}:{proxy_data.port}"
            action_log_data.proxy = proxy_body

            proxy_set_up_status = False

            if proxy_data.is_mobile is True and self.app_config.mobile_proxy_rotation is True:
                rotation_link = self.app_config.mobile_proxy_rotation_link
                if not rotation_link:
                    err_msg = "Mobile proxy rotation link is not set (go to app_config.json)"
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
                    f"Proxy valid, using {wallet_data.proxy.host}:{wallet_data.proxy.port} (ip: {current_ip})")

            if proxy_set_up_status is False:
                action_logger = ActionLogger(action_data=action_log_data)
                action_logger.log_error()
                return False

        self.action_storage.update_current_action(action_data=action_log_data)
        wallet_address = self.get_addr_from_private_key(wallet_data.private_key)
        key_pair = get_key_pair_from_pk(wallet_data.private_key)

        proxy_unit: Optional[aiohttp.typedefs.StrOrURL] = proxies.get('http://') if proxies else None

        connector = aiohttp.TCPConnector(limit=10)
        custom_session = CustomSession(proxy=proxy_unit, connector=connector)
        client = FullNodeClient(node_url=base_url, session=custom_session)

        account = Account(
            address=wallet_address,
            client=client,
            key_pair=key_pair,
            chain=StarknetChainId.MAINNET
        )

        if self.module_name == enums.ModuleName.JEDI_SWAP:
            if self.module_type == enums.ModuleType.SWAP:
                module = JediSwap(
                    account=account,
                    config=self.config
                )
                execution_status = await module.send_swap_txn()

            elif self.module_type == enums.ModuleType.LIQUIDITY_ADD:
                module = JediSwapAddLiquidity(
                    account=account,
                    config=self.config
                )
                execution_status = await module.send_add_liq_txn()

            elif self.module_type == enums.ModuleType.LIQUIDITY_REMOVE:
                module = JediSwapRemoveLiquidity(
                    account=account,
                    config=self.config
                )
                execution_status = await module.send_remove_liq_txn()

        elif self.module_name == enums.ModuleName.MY_SWAP:
            if self.module_type == enums.ModuleType.SWAP:
                module = MySwap(
                    account=account,
                    config=self.config
                )
                execution_status = await module.send_swap_txn()

            elif self.module_type == enums.ModuleType.LIQUIDITY_ADD:
                module = MySwapAddLiquidity(
                    account=account,
                    config=self.config
                )
                execution_status = await module.send_add_liq_txn()

            elif self.module_type == enums.ModuleType.LIQUIDITY_REMOVE:
                module = MySwapRemoveLiquidity(
                    account=account,
                    config=self.config
                )
                execution_status = await module.send_remove_liq_txn()

        elif self.module_name == enums.ModuleName.DEPLOY:
            if self.module_type == enums.PrivateKeyType.argent:
                module = DeployArgent(
                    account=account,
                    config=self.config,
                    private_key=wallet_data.private_key
                )
                execution_status = await module.send_deploy_txn()

            elif self.module_type == enums.PrivateKeyType.braavos:
                module = DeployBraavos(
                    account=account,
                    config=self.config,
                    private_key=wallet_data.private_key
                )
                execution_status = await module.send_deploy_txn()

        elif self.module_name == enums.ModuleName.AVNU:
            if self.module_type == enums.ModuleType.SWAP:
                module = AvnuSwap(
                    account=account,
                    config=self.config
                )
                execution_status = await module.send_swap_txn()

        elif self.module_name == enums.ModuleName.SITHSWAP:
            if self.module_type == enums.ModuleType.SWAP:
                module = SithSwap(
                    account=account,
                    config=self.config
                )
                execution_status = await module.send_swap_txn()

            elif self.module_type == enums.ModuleType.LIQUIDITY_ADD:
                module = SithSwapAddLiquidity(
                    account=account,
                    config=self.config
                )
                execution_status = await module.send_add_liq_txn()

            elif self.module_type == enums.ModuleType.LIQUIDITY_REMOVE:
                module = SithSwapRemoveLiquidity(
                    account=account,
                    config=self.config
                )
                execution_status = await module.send_remove_liq_txn()

        elif self.module_name == enums.ModuleName.K10SWAP:
            if self.module_type == enums.ModuleType.SWAP:
                module = K10Swap(
                    account=account,
                    config=self.config
                )
                execution_status = await module.send_swap_txn()

        elif self.module_name == enums.ModuleName.IDENTITY:
            if self.module_type == enums.ModuleType.MINT:
                module = IdentityMint(
                    account=account,
                    config=self.config
                )
                execution_status = await module.send_mint_txn()

        elif self.module_name == enums.ModuleName.ZKLEND:
            if self.module_type == enums.ModuleType.SUPPLY:
                module = ZkLendSupply(
                    account=account,
                    config=self.config
                )
                execution_status = await module.send_supply_txn()

            elif self.module_type == enums.ModuleType.WITHDRAW:
                module = ZkLendWithdraw(
                    account=account,
                    config=self.config
                )
                execution_status = await module.send_withdraw_txn()

        elif self.module_type == enums.ModuleType.TEST:
            module = ModulesTest(
                account=account,
                config=self.config
            )
            execution_status = await module.test()

        else:
            await connector.close()
            raise ValueError(f"Invalid module name: {self.module_name}")

        if self.config.test_mode is False:
            ActionLogger.log_action_from_storage()

        await connector.close()

        return execution_status
