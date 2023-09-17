import time
import random
import multiprocessing as mp
from typing import Optional, List, Callable

from loguru import logger

from modules.module_executor import ModuleExecutor
from src.schemas.tasks.base.base import TaskBase
from src.internal_queue import InternalQueue


class TasksExecutor:
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        self.running = False
        self.process: Optional[mp.Process] = None

        self.tasks_queue = InternalQueue()

    def process_task(self, task: "TaskBase"):
        """
        Process a task, executing on task receiving
        :param task: task to process
        """
        # module_executor = ModuleExecutor(task)
        logger.debug(f"Processing task: {task}")    # TODO: DODELATE

    def push_tasks(self, tasks: List[TaskBase], shuffle: bool = False):
        self.tasks_queue.push_tasks(tasks, shuffle)

    def loop(self):
        while self.running:
            try:
                task = self.tasks_queue.get_task()

                if task is None:
                    time.sleep(0.1)
                    continue

                self.process_task(task)

                time_to_sleep = random.randint(
                    task.min_delay_sec,
                    task.max_delay_sec
                )

                # time.sleep(time_to_sleep) # TODO: Hardcoded time

                time.sleep(3)

            except Exception as ex:
                logger.error(ex)
                logger.exception(ex)

    def stop(self):
        logger.info("Stopping tasks executor")
        self.running = False
        self.process.terminate()
        self.process.join()

    def run(self):

        logger.info("Starting tasks executor")

        self.running = True
        self.process = mp.Process(target=self.loop)
        self.process.start()
