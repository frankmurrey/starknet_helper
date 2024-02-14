import random

from modules.base import SwapModuleBase
from contracts.tokens.main import Tokens

from src.schemas import tasks
from src.schemas.wallet_data import WalletData
from src.schemas.tasks.base.swap import SwapTaskBase
from src.schemas.action_models import ModuleExecutionResult

SWAP_TASKS = [
    tasks.SithSwapTask,
    tasks.JediSwapTask,
    tasks.MySwapTask,
    tasks.K10SwapTask,
    tasks.AvnuSwapTask,
    tasks.StarkExSwapTask
]


class RandomSwap(SwapModuleBase):
    def __init__(
            self,
            account,
            task: SwapTaskBase,
            wallet_data: WalletData,
    ):
        super().__init__(
            account=account,
            task=task,
            wallet_data=wallet_data,
        )
        random_task_class = random.choice(SWAP_TASKS)
        task_dict = self.task.dict(exclude={"module_name",
                                            "module_type",
                                            "module"})
        random_task: SwapTaskBase = random_task_class(**task_dict)
        self.task = random_task

        if random_task.random_y_coin:
            protocol_coins_obj = Tokens().get_tokens_by_protocol(random_task.module_name)
            protocol_coins = [coin.symbol for coin in protocol_coins_obj]
            protocol_coins.remove(random_task.coin_x.lower())
            random_task.coin_y = random.choice(protocol_coins)

            self.task = random_task

            self.coin_x = self.tokens.get_by_name(self.task.coin_x)
            self.coin_y = self.tokens.get_by_name(self.task.coin_y)

            self.initial_balance_x_wei = None
            self.initial_balance_y_wei = None

            self.token_x_decimals = None
            self.token_y_decimals = None

    async def try_send_txn(
            self,
            retries: int = 1,
    ) -> ModuleExecutionResult:
        """
        Try to send transaction
        :param retries:
        :return:
        """

        await self.set_fetched_tokens_data()

        module = self.task.module(
            account=self.account,
            task=self.task,
            wallet_data=self.wallet_data,
        )

        return await module.try_send_txn(retries=retries)

