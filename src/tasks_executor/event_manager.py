import time
import queue
import threading as th
import multiprocessing as mp
from typing import Optional, Union
from typing import Callable
from typing import Tuple

from loguru import logger

from src.schemas.tasks import TaskBase
from src.schemas.wallet_data import WalletData
from src.schemas import event_item
from src.internal_queue import InternalQueue


def state_setter(obj: "TasksExecEventManager", state: dict):
    obj.running = state["running"]

    obj.started_events_queue = state["started_events_queue"]
    obj.completed_events_queue = state["completed_events_queue"]


class TasksExecEventManager:

    event_item_callback_map = {
        event_item.WalletStartedEventItem: "_on_wallet_started",
        event_item.TaskStartedEventItem: "_on_task_started",
        event_item.WalletCompletedEventItem: "_on_wallet_completed",
        event_item.TaskCompletedEventItem: "_on_task_completed",
    }

    def __init__(self):
        self.running = mp.Event()
        self.listening_thread: Optional[th.Thread] = None

        self.started_events_queue = InternalQueue[Union[
            event_item.WalletStartedEventItem,
            event_item.TaskStartedEventItem,
        ]]()

        self.completed_events_queue = InternalQueue[Union[
            event_item.WalletCompletedEventItem,
            event_item.TaskCompletedEventItem,
        ]]()

        self._on_wallet_started: Optional[Callable[[WalletData], None]] = self.pseudo_callback
        self._on_task_started: Optional[Callable[[TaskBase, WalletData], None]] = self.pseudo_callback

        self._on_wallet_completed: Optional[Callable[[WalletData], None]] = self.pseudo_callback
        self._on_task_completed: Optional[Callable[[TaskBase, WalletData], None]] = self.pseudo_callback

    def pseudo_callback(self, *args, **kwargs):
        """
        Placeholder method for a completed callback function.
        """
        logger.warning("Pseudo completed callback called.")

    # CALLBACKS SETTERS
    def on_wallet_started(self, callback: Callable[[WalletData], None]):
        """
        Set a callback function to be called when a wallet is started.

        Args:
            callback (Callable[[WalletData], None]): The callback function to be called when a wallet is started.
        """
        self._on_wallet_started = callback

    def on_task_started(self, callback: Callable[[TaskBase, WalletData], None]):
        """
        Set a callback function to be called when a task is started.

        Args:
            callback (Callable[[TaskBase, WalletData], None]): The callback function to be called when a task is started.
        """
        self._on_task_started = callback

    def on_wallet_completed(self, callback: Callable[[WalletData], None]):
        """
        Set a callback function to be called when a wallet is completed.

        Args:
            callback (Callable[[WalletData], None]): The callback function to be called when a wallet is completed.
        """
        self._on_wallet_completed = callback

    def on_task_completed(self, callback: Callable[[TaskBase, WalletData], None]):
        """
        Set a callback function to be called when a task is completed.

        Args:
            callback (Callable[[TaskBase, WalletData], None]): The callback function to be called when a task is completed.
        """
        self._on_task_completed = callback

    # EVENT CREATORS
    def set_wallet_started(self, wallet: WalletData):
        """
        Add a wallet to the 'wallets_started_queue'.

        Args:
            wallet (WalletData): The wallet to be added to the queue.
        """
        self.started_events_queue.put_nowait(
            event_item.WalletStartedEventItem(wallet=wallet)
        )

    def set_task_started(self, task: TaskBase, wallet: WalletData):
        """
        Add a task and associated wallet to the 'tasks_started_queue'.

        Args:
            task (TaskBase): The task that was started.
            wallet (WalletData): The wallet associated with the task.
        """
        self.started_events_queue.put_nowait(
            event_item.TaskStartedEventItem(task=task, wallet=wallet)
        )

    def set_wallet_completed(self, wallet: WalletData):
        """
        Add a wallet to the 'wallets_completed_queue'.

        Args:
            wallet (WalletData): The wallet to be added to the queue.
        """
        self.completed_events_queue.put_nowait(
            event_item.WalletCompletedEventItem(wallet=wallet)
        )

    def set_task_completed(self, task: TaskBase, wallet: WalletData):
        """
        Add a task and associated wallet to the 'tasks_completed_queue'.

        Args:
            task (TaskBase): The task that was completed.
            wallet (WalletData): The wallet associated with the task.
        """
        self.completed_events_queue.put_nowait(
            event_item.TaskCompletedEventItem(task=task, wallet=wallet)
        )

    def _process_queue_item(self, queue_name: str):
        """
        Process an item from a queue and call the given callback function.

        Args:
            queue_name (str): The name of the queue to process.
            callback (Callable): The callback function to call with the queue item.
        """
        try:
            _queue: InternalQueue = getattr(self, queue_name)

            queue_item: Union[
                event_item.WalletStartedEventItem,
                event_item.TaskStartedEventItem,
                event_item.WalletCompletedEventItem,
                event_item.TaskCompletedEventItem,
            ] = _queue.get_nowait()

            if not self.running.is_set():
                return

            callback = getattr(self, self.event_item_callback_map[queue_item.__class__])
            callback(*queue_item.get_data())

        except queue.Empty:
            time.sleep(0.1)

    def listen_for_event_items(self):
        """
        Listen for started and completed tasks and wallets
        """
        logger.debug("Listening thread started")

        while self.running.is_set():
            self._process_queue_item("started_events_queue")
            self._process_queue_item("completed_events_queue")

        logger.debug("Listening thread stopped")

    def start(self):
        """
        Start the listening thread
        """
        self.running.set()
        self.listening_thread = th.Thread(target=self.listen_for_event_items)
        self.listening_thread.start()

    def stop(self):
        """
        Stop the listening thread
        """
        self.running.clear()

    def __reduce__(self):
        return (
            object.__new__,
            (type(self),),
            {
                "running": self.running,

                # queues
                "started_events_queue": self.started_events_queue,
                "completed_events_queue": self.completed_events_queue,
            },
            None,
            None,
            state_setter,
        )
