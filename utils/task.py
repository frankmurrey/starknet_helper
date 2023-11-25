import random
from typing import Optional
from typing import TYPE_CHECKING

import config

if TYPE_CHECKING:
    from src.schemas.tasks.base.base import TaskBase
    from src.schemas.action_models import ModuleExecutionResult


def get_time_to_sleep(
        task: "TaskBase",
        task_result: Optional["ModuleExecutionResult"],
) -> int:
    if not task_result or task.test_mode:
        return config.DEFAULT_DELAY_SEC
    else:
        return random.randint(
            task.min_delay_sec,
            task.max_delay_sec
        )
