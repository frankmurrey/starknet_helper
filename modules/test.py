from modules.base import ModuleBase
from src.schemas.configs.app_config import AppConfigSchema

from starknet_py.net.http_client import HttpMethod


class ModulesTest(ModuleBase):
    def __init__(
            self,
            account,
            config=None):
        super().__init__(client=account.client)

        self._account = account
        self._config = config

        self.app_config: AppConfigSchema = self.storage.app_config

    async def test(self):
        gas_price = await self.get_eth_mainnet_gas_price()
        print(gas_price)
