from typing import List

from src.tasks_executor.base import TaskExecutorBase
from src.tasks_executor.multithread import TaskExecutorMultiThread
from src.tasks_executor.singlethread import TaskExecutorSingleThread
from src.schemas.wallet_data import WalletData
from src.schemas.tasks import TaskBase


class TaskExecutor:
    """
    Wrapper for tasks executor
    """
    def __init__(self):
        self.task_executor_single_thread = TaskExecutorSingleThread()
        self.task_executor_multithread = TaskExecutorMultiThread()

    def process(
            self,
            wallets: List["WalletData"],
            tasks: List["TaskBase"],

            shuffle_wallets: bool = False,
            shuffle_tasks: bool = False,

            multithread: bool = False,
    ):
        kwargs = {
            "wallets": wallets,
            "tasks": tasks,

            "shuffle_wallets": shuffle_wallets,
            "shuffle_tasks": shuffle_tasks,
        }
        if multithread:
            self.task_executor_multithread.process(**kwargs)
        else:
            self.task_executor_single_thread.process(**kwargs)

    def stop(self):
        self.task_executor_single_thread.stop()
        self.task_executor_multithread.stop()


task_executor = TaskExecutor()
