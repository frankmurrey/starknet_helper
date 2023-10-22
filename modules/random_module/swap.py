import random
from modules.base import SwapModuleBase
from src.schemas.action_models import ModuleExecutionResult
from src.schemas.tasks.base.swap import SwapTaskBase
from src.schemas import tasks

SWAP_TASKS = [
    tasks.LiquidSwapSwapTask,
    tasks.PancakeSwapTask,
]


class RandomSwap(SwapModuleBase):
    def try_send_txn(
            self,
            retries: int = 1,
    ) -> ModuleExecutionResult:
        """
        Try to send transaction
        :param retries:
        :return:
        """
        random_task_class = random.choice(SWAP_TASKS)
        task_dict = self.task.dict(exclude={"module_name",
                                            "module_type",
                                            "module"})
        random_task: SwapTaskBase = random_task_class(**task_dict)

        module = random_task.module(
            account=self.account,
            task=random_task,
            base_url=self.base_url,
            proxies=self.proxies,
        )
        return module.try_send_txn(retries=retries)

