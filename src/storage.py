from src.paths import APP_CONFIG_FILE
from src.schemas.configs.app_config import AppConfigSchema
from utlis.file_manager import FileManager


class Storage:
    __instance = None

    class __Singleton:

        def __init__(self):
            self.__wallets_data = FileManager.get_wallets_from_files()
            self.__app_config = self.__load_app_config()
            self.__wallet_balances = []

        def set_wallets_data(self, value):
            self.__wallets_data = value

        def get_wallets_data(self):
            return self.__wallets_data

        def get_wallet_balances(self):
            return self.__wallet_balances

        def get_app_config(self) -> AppConfigSchema:
            return self.__app_config

        def __load_app_config(self):
            try:
                config_file_data = FileManager.read_data_from_json_file(APP_CONFIG_FILE)
                return AppConfigSchema(**config_file_data)
            except Exception as e:
                raise e

        def append_wallet_balance(self, value):
            self.__wallet_balances.append(value)

        def get_wallet_balances(self):
            return self.__wallet_balances

        def reset_wallet_balances(self):
            self.__wallet_balances = []

        def update_app_config(self, config: AppConfigSchema):
            self.__app_config = config

    def __new__(cls):
        if not Storage.__instance:
            Storage.__instance = Storage.__Singleton()
        return Storage.__instance

