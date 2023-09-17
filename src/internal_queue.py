import random
import multiprocessing as mp
from typing import Optional, List
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.schemas.tasks.base.base import TaskBase


class InternalQueue:
    """
    InternalQueue class wraps the standard Python Queue to provide custom functionality.
    """

    def __init__(self):
        self._queue = mp.Queue()

    def get_task(self) -> Optional["TaskBase"]:
        """
        Get the next task from the queue if available.

        :returns: Task, or None if the queue is empty.
        :rtype: Task
        """

        if not self._queue.empty():
            return self._queue.get_nowait()
        return None

    def add_task(self, task: "TaskBase") -> None:
        """
        Add a task to the queue.

        :param TaskBase task: The task to add in the queue.
        """
        self._queue.put(task)

    def push_tasks(self, tasks: List["TaskBase"], shuffle: bool = False) -> None:
        """
        Add multiple tasks to the queue.

        :param List[TaskBase] tasks: The tasks to add in the queue.
        :param bool shuffle: Whether to shuffle the tasks
        """
        if shuffle:
            random.shuffle(tasks)
        for task in tasks:
            self._queue.put(task)
