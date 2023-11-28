import time
import asyncio
import threading as th
from typing import Optional, List

from loguru import logger

from src.schemas.app_config import AppConfigSchema
from src.schemas.tasks.base.base import TaskBase
from src.schemas.wallet_data import WalletData
from src.storage import Storage
from src.tasks_executor.main import TaskExecutor
from src.logger import configure_logger

from utils.repr import misc as repr_misc_utils
from utils.repr import message as repr_message_utils
from utils import task as task_utils

import config


def clear_threads(
    wallet_threads: List[th.Thread],
    max_threads_num: int = 0,
):
    """
    Clear executed wallet threads
    Args:
        wallet_threads: list of threads
        max_threads_num: max threads
    """
    while len(wallet_threads) >= max_threads_num:
        for thread_index, thread in enumerate(wallet_threads):
            if not thread.is_alive():
                wallet_threads.pop(thread_index)
        time.sleep(0.1)


class ThreadedTaskExecutor(TaskExecutor):
    def __init__(
            self
    ):
        super().__init__()

        self.lock: Optional[th.Lock] = None

    def _start_processing(
            self,
            wallets: List["WalletData"],
            tasks: List["TaskBase"],
    ):
        """
        Start processing async
        """

        Storage().update_app_config(config=AppConfigSchema(**self._app_config_dict))
        configure_logger()
        self.lock = th.Lock()

        wallet_threads = []
        for wallet_index, wallet in enumerate(wallets):
            clear_threads(wallet_threads, max_threads_num=config.DEFAULT_WALLETS_THREADS_NUM)
            is_last_wallet = wallet_index == len(wallets) - 1
            loop = asyncio.get_event_loop()

            thread = th.Thread(
                target=self.process_wallet,
                args=(
                    wallet,
                    wallet_index,
                    tasks,

                    is_last_wallet,

                    loop,
                )
            )

            if not is_last_wallet:
                time.sleep(config.DEFAULT_DELAY_SEC)

            thread.start()
            wallet_threads.append(thread)

        clear_threads(wallet_threads)
        logger.success("All wallets processed")

    def process_wallet(
            self,
            wallet: "WalletData",
            wallet_index: int,
            tasks: List["TaskBase"],

            is_last_wallet: bool = False,

            loop: Optional[asyncio.AbstractEventLoop] = None,
    ):
        """
        Process a wallet
        Args:
            wallet: wallet to process
            wallet_index: index of wallet
            tasks: list of tasks to process
            is_last_wallet: is current wallet the last
            loop: asyncio loop
        """

        asyncio.set_event_loop(loop)

        self.wait_for_unlock()

        with self.lock:
            self.event_manager.set_wallet_started(wallet)
            repr_misc_utils.print_wallet_execution(wallet, wallet_index)

        for task_index, task in enumerate(tasks):

            task_result = self.process_task(
                task=task,
                wallet_index=wallet_index,
                wallet=wallet,
            )

            time_to_sleep = task_utils.get_time_to_sleep(task=task, task_result=task_result)
            is_last_task = task_index == len(tasks) - 1

            if not is_last_task:
                logger.info(repr_message_utils.task_exec_sleep_message(time_to_sleep))
                time.sleep(time_to_sleep)

        self.event_manager.set_wallet_completed(wallet)

    def process_task(
            self,
            task: "TaskBase",
            wallet_index: int,
            wallet: "WalletData",
    ):
        with self.lock:
            task_result = super().process_task(
                task=task,
                wallet_index=wallet_index,
                wallet=wallet,
            )

        return task_result

    def wait_for_unlock(self):
        while self.lock.locked():
            time.sleep(0.1)


threaded_task_executor = ThreadedTaskExecutor()
