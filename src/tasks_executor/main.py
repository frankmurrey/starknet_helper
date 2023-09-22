import time
import random
import queue
import asyncio
import threading as th
import multiprocessing as mp
from typing import Optional, List, Callable

from loguru import logger

import config
from src import enums
from modules.module_executor import ModuleExecutor
from src.schemas.tasks.base.base import TaskBase
from src.schemas.wallet_data import WalletData
from src.logger import configure_logger
from utils.repr.misc import print_wallet_execution


class TasksExecutor:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(TasksExecutor, cls).__new__(cls, *args, **kwargs)

        return cls.__instance

    def __init__(
            self,
            on_wallet_started: Optional[Callable[[WalletData], None]] = None,
            on_task_started: Optional[Callable[[TaskBase, WalletData], None]] = None,
            on_task_completed: Optional[Callable[[TaskBase, WalletData], None]] = None,
            on_wallet_completed: Optional[Callable[[WalletData], None]] = None
    ):
        self.running = False
        self.main_process: Optional[mp.Process] = None
        self.started_thread: Optional[th.Thread] = None
        self.completed_thread: Optional[th.Thread] = None

        self.start_event = mp.Event()
        self.stop_event = mp.Event()
        self.kill_event = mp.Event()

        self.wallets_queue = mp.Queue()
        self.tasks_queue = mp.Queue()

        self.started_wallets_queue = mp.Queue()
        self.started_tasks_queue = mp.Queue()

        self.completed_wallets_queue = mp.Queue()
        self.completed_tasks_queue = mp.Queue()

        self._on_wallet_started = (
            on_wallet_started if on_wallet_started is not None
            else self.pseudo_completed_callback
        )

        self._on_task_started = (
            on_task_started if on_task_started is not None
            else self.pseudo_completed_callback
        )

        self._on_task_completed = (
            on_task_completed if on_task_completed is not None
            else self.pseudo_completed_callback
        )
        self._on_wallet_completed = (
            on_wallet_completed if on_wallet_completed is not None
            else self.pseudo_completed_callback
        )

        self.wallets_to_process = []
        self.tasks_to_process = []

    def pseudo_completed_callback(self, *args, **kwargs):
        pass

    def on_wallet_started(self, callback: Callable[[WalletData], None]):
        self._on_wallet_started = callback

    def on_task_started(self, callback: Callable[[TaskBase, WalletData], None]):
        self._on_task_started = callback

    def on_task_completed(self, callback: Callable[[TaskBase, WalletData], None]):
        self._on_task_completed = callback

    def on_wallet_completed(self, callback: Callable[[WalletData], None]):
        self._on_wallet_completed = callback

    def process_task(self, task: "TaskBase", wallet: "WalletData", ):
        """
        Process a task, executing on task receiving
        Args:
            task: task to process
            wallet: wallet for task
        """
        logger.debug(f"Processing task: {task.task_id} with wallet: {wallet.name}")
        module_executor = ModuleExecutor(task=task, wallet=wallet)
        return asyncio.run(module_executor.start())

    def loop(self):
        """
        Main loop
        """
        configure_logger()
        logger.debug("Starting main loop")

        while self.running:
            try:
                self.start_event.wait()

                try:
                    self.wallets_to_process = self.wallets_queue.get_nowait()
                except queue.Empty:
                    time.sleep(0.1)

                try:
                    self.tasks_to_process = self.tasks_queue.get_nowait()
                except queue.Empty:
                    time.sleep(0.1)

                if self.is_killed(clear=True):
                    break

                if self.is_stopped(clear=True):
                    break

                if not len(self.wallets_to_process) or not len(self.tasks_to_process):
                    continue

                for wallet_index, wallet in enumerate(self.wallets_to_process):
                    self.started_wallets_queue.put_nowait(wallet)

                    print_wallet_execution(wallet, wallet_index)

                    self.sleep(0.1)

                    for task_index, task in enumerate(self.tasks_to_process):
                        task: TaskBase

                        task.task_status = enums.TaskStatus.PROCESSING
                        self.started_tasks_queue.put_nowait((task, wallet))

                        logger.debug(f"Processing task: {task.task_id}")

                        task_result = self.process_task(
                            task=task,
                            wallet=wallet
                        )

                        if self.is_killed():
                            break

                        if self.is_stopped():
                            break

                        if task_result:
                            task.task_status = enums.TaskStatus.SUCCESS
                        else:
                            task.task_status = enums.TaskStatus.FAILED

                        self.completed_tasks_queue.put_nowait((task, wallet))

                        if not task_result or task.test_mode:
                            time_to_sleep = config.DEFAULT_DELAY_SEC
                        else:
                            time_to_sleep = random.randint(
                                task.min_delay_sec,
                                task.max_delay_sec
                            )

                        is_last = all([
                            wallet_index == len(self.wallets_to_process) - 1,
                            task_index == len(self.tasks_to_process) - 1
                        ])

                        if not is_last:
                            logger.info(f"Time to sleep for {time_to_sleep} seconds...")
                            self.sleep(time_to_sleep)

                        else:
                            logger.success(f"All wallets and tasks completed!")

                    self.completed_wallets_queue.put_nowait(wallet)

                self.wallets_to_process = []
                self.tasks_to_process = []

            except KeyboardInterrupt:
                self.running = False
                break

            except Exception as ex:
                logger.error(ex)
                logger.exception(ex)

        self.wallets_to_process = []
        self.tasks_to_process = []

    def sleep(self, secs: float):
        """
        Sleep for some time
        Args:
            secs: time to sleep
        """
        wakeup_time = time.time() + secs

        while time.time() < wakeup_time:
            if self.is_killed():
                break

            if self.is_stopped():
                break

            time.sleep(0.1)

    def is_killed(self, clear: bool = False):
        if self.kill_event.is_set():
            if clear:
                self.kill_event.clear()
            self.running = False
            self.tasks_to_process = []
            self.wallets_to_process = []
            return True
        return False

    def is_stopped(self, clear: bool = False):
        if self.stop_event.is_set():
            if clear:
                self.stop_event.clear()
            # self.running = False
            self.tasks_to_process = []
            self.wallets_to_process = []
            return True
        return False

    def listen_for_started_items(self):
        """
        Listen for started tasks and wallets
        """
        while self.running:
            try:
                started_task, current_wallet = self.started_tasks_queue.get_nowait()
                self._on_task_started(started_task, current_wallet)
            except queue.Empty:
                time.sleep(0.1)

            try:
                started_wallet = self.started_wallets_queue.get_nowait()
                self._on_wallet_started(started_wallet)
            except queue.Empty:
                time.sleep(0.1)

    def listen_for_completed_items(self):
        """
        Listen for completed tasks and wallets
        """
        while self.running:
            try:
                completed_task, current_wallet = self.completed_tasks_queue.get_nowait()
                self._on_task_completed(completed_task, current_wallet)
            except queue.Empty:
                time.sleep(0.1)

            try:
                completed_wallet = self.completed_wallets_queue.get_nowait()
                self._on_wallet_completed(completed_wallet)
            except queue.Empty:
                time.sleep(0.1)

    def push_wallets(self, wallets: List[WalletData], shuffle: bool = False):
        """
        Push wallets to queue
        Args:
            wallets: wallets to push
            shuffle: whether to shuffle
        """

        if shuffle:
            random.shuffle(wallets)

        self.wallets_queue.put(wallets)

    def push_tasks(self, tasks: List[TaskBase], shuffle: bool = False):
        """
        Push tasks to tasks executor
        Args:
            tasks: tasks to push
            shuffle: whether to shuffle
        """

        if shuffle:
            random.shuffle(tasks)

        self.tasks_queue.put(tasks)

    def stop_tasks_processing(self):
        """
        Stop tasks processing
        """
        self.stop_event.set()
        self.start_event.clear()
        logger.warning("Tasks processing stopped")

    def start_tasks_processing(self):
        """
        Start tasks processing
        """
        self.stop_event.clear()
        self.start_event.set()

    def run(self):
        """
        Run tasks executor
        """
        logger.debug("Starting tasks executor")

        self.running = True

        _on_wallet_started = self._on_wallet_started
        _on_task_started = self._on_task_started

        _on_task_completed = self._on_task_completed
        _on_wallet_completed = self._on_wallet_completed

        self._on_wallet_started = self.pseudo_completed_callback
        self._on_task_started = self.pseudo_completed_callback

        self._on_task_completed = self.pseudo_completed_callback
        self._on_wallet_completed = self.pseudo_completed_callback

        self.main_process = mp.Process(target=self.loop)
        self.main_process.start()
        # self.start_event.set()

        self._on_wallet_started = _on_wallet_started
        self._on_task_started = _on_task_started

        self._on_task_completed = _on_task_completed
        self._on_wallet_completed = _on_wallet_completed

        self.started_thread = th.Thread(target=self.listen_for_started_items)
        self.started_thread.start()

        self.completed_thread = th.Thread(target=self.listen_for_completed_items)
        self.completed_thread.start()

    def kill(self):
        """
        Kill tasks executor
        """
        logger.debug("Killing tasks executor")

        self.wallets_to_process = []
        self.tasks_to_process = []

        self.running = False
        self.kill_event.set()


tasks_executor = TasksExecutor()


if __name__ == '__main__':
    tasks_executor.run()

    time.sleep(5)

    tasks_executor.kill()
