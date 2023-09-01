from typing import List

from loguru import logger

from src import paths
from src.schemas.configs.app_config import AppConfigSchema
from utlis.file_manager import FileManager


class Storage:
    __instance = None

    class __Singleton:

        def __init__(self):
            self.__wallets_data = FileManager.get_wallets_from_files()
            self.__app_config: AppConfigSchema = self.__load_app_config()
            self.__wallet_balances = []

        def set_wallets_data(self, value):
            self.__wallets_data = value

        @property
        def wallets_data(self):
            return self.__wallets_data

        @property
        def wallet_balances(self) -> List:
            return self.__wallet_balances

        @property
        def app_config(self) -> AppConfigSchema:
            return self.__app_config

        @property
        def wallet_balances(self):
            return self.__wallet_balances

        def __load_app_config(self) -> AppConfigSchema:
            try:
                config_file_data = FileManager.read_data_from_json_file(paths.APP_CONFIG_FILE)
                return AppConfigSchema(**config_file_data)
            except Exception as e:
                logger.error(f"Error while loading app config: {e}")
                logger.exception(e)

        def append_wallet_balance(self, value):
            self.__wallet_balances.append(value)

        def reset_wallet_balances(self):
            self.__wallet_balances = []

        def update_app_config(self, config: AppConfigSchema):
            self.__app_config = config

    def __new__(cls):
        if not Storage.__instance:
            Storage.__instance = Storage.__Singleton()
        return Storage.__instance

