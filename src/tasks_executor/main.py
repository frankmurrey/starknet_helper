import time
import random
import queue
import threading as th
import multiprocessing as mp
from typing import Optional, List, Callable

from loguru import logger

from modules.module_executor import ModuleExecutor
from src.schemas.tasks.base.base import TaskBase
from src.schemas.wallet_data import WalletData


class TasksExecutor:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(
            self,
            on_task_completed: Optional[Callable[[TaskBase, WalletData], None]] = None,
            on_wallet_completed: Optional[Callable[[WalletData], None]] = None
    ):
        self.running = False
        self.main_process: Optional[mp.Process] = None
        self.completed_thread: Optional[th.Thread] = None

        self.stop_event = mp.Event()
        self.kill_event = mp.Event()

        self.wallets_queue = mp.Queue()
        self.tasks_queue = mp.Queue()

        self.completed_wallets_queue = mp.Queue()
        self.completed_tasks_queue = mp.Queue()

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

    def process_task(self, task: "TaskBase", wallet: "WalletData", ):
        """
        Process a task, executing on task receiving
        Args:
            task: task to process
            wallet: wallet for task
        """
        # module_executor = ModuleExecutor(task)
        logger.debug(f"Processing task: {task.task_id} with wallet: {wallet.name}")    # TODO: DODELATE TASKS PROCESSING

    def loop(self):
        """
        Main loop
        """
        logger.debug("Starting main loop")

        while self.running:
            try:
                logger.debug("Waiting for wallets")
                self.wallets_to_process = self.wallets_queue.get()

                logger.debug("Waiting for tasks")
                self.tasks_to_process = self.tasks_queue.get()

                if not len(self.tasks_to_process) or not len(self.wallets_to_process):
                    time.sleep(1)
                    continue

                logger.debug("Processing tasks")

                for wallet in self.wallets_to_process:
                    for task in self.tasks_to_process:

                        if self.kill_event.wait(0.1):
                            self.running = False
                            break

                        if self.stop_event.wait(0.1):
                            break

                        self.process_task(
                            task=task,
                            wallet=wallet
                        )
                        self.completed_tasks_queue.put_nowait((task, wallet))

                        if self.kill_event.wait(0.1):
                            self.running = False
                            break

                        time_to_sleep = random.randint(
                            task.min_delay_sec,
                            task.max_delay_sec
                        )

                        time.sleep(time_to_sleep)

                    self.completed_wallets_queue.put_nowait(wallet)

                self.wallets_to_process = []
                self.tasks_to_process = []

            except KeyboardInterrupt:
                self.kill()

            except Exception as ex:
                logger.error(ex)
                logger.exception(ex)

        self.wallets_to_process = []
        self.tasks_to_process = []

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

    def run(self):
        """
        Run tasks executor
        """
        logger.debug("Starting tasks executor")

        self.running = True

        _on_task_completed = self._on_task_completed
        _on_wallet_completed = self._on_wallet_completed
        self._on_task_completed = self.pseudo_completed_callback
        self._on_wallet_completed = self.pseudo_completed_callback

        self.main_process = mp.Process(target=self.loop)
        self.main_process.start()

        self._on_task_completed = _on_task_completed
        self._on_wallet_completed = _on_wallet_completed

        self.completed_thread = th.Thread(target=self.listen_for_completed_items)
        self.completed_thread.start()

    def kill(self):
        """
        Kill tasks executor
        """
        logger.debug("Stopping tasks executor")

        self.wallets_to_process = []
        self.tasks_to_process = []

        self.running = False
        self.kill_event.set()
