from src.schemas.tasks.base import TaskBase


class MintTaskBase(TaskBase):
    amount: int = 1

    @property
    def action_info(self):
        return f""
