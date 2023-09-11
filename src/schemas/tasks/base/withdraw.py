from typing import Union

from src.schemas.tasks.base import TaskBase


class WithdrawTaskBase(TaskBase):
    coin_to_withdraw: Union[str]
