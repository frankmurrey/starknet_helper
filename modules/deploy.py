import time
import random

from contracts.tokens.main import Tokens

from modules.base import StarkBase

from src.schemas.configs.deploy import DeployConfigSchema

from starknet_py.net.account.account import Account

from loguru import logger


class Deploy(StarkBase):
    config: DeployConfigSchema
    account: Account

    def __init__(self,
                 account,
                 config):
        super().__init__(client=account.client)

        self.config = config
        self.account = account

    def build_txn_payload_calls(self):
        pass



