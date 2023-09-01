import os
import json
from typing import Union, List

from loguru import logger

from src import paths
from src.schemas.proxy_data import ProxyData
from src.schemas.wallet_data import WalletData

import config
from src.wallet_manager import WalletManager


class FileManager:

    def __init__(self):
        pass

    @staticmethod
    def read_abi_from_file(file_path: str) -> Union[dict, None]:
        # TODO: possibly excessive method

        filename = os.path.basename(file_path)

        if not os.path.exists(file_path):
            logger.error(f"File \"{filename}\" does not exist")
            return None

        try:
            with open(file_path, "r") as file:
                return json.loads(file.read())

        except json.decoder.JSONDecodeError as e:
            logger.error(f"File \"{filename}\" is not a valid JSON file")

        except Exception as e:
            logger.error(f"Error while reading file \"{file_path}\": {e}")
            logger.exception(e)
            return None

    @staticmethod
    def read_data_from_json_file(file_path) -> Union[dict, None]:
        filename = os.path.basename(file_path)

        if not os.path.exists(file_path):
            logger.error(f"File \"{filename}\" does not exist")
            return None

        try:
            with open(file_path, "r") as file:
                return json.load(file)

        except json.decoder.JSONDecodeError as e:
            logger.error(f"File \"{filename}\" is not a valid JSON file")

        except Exception as e:
            logger.error(f"Error while reading file \"{file_path}\": {e}")
            logger.exception(e)
            return None

        return None

    @staticmethod
    def read_data_from_txt_file(file_path: str) -> Union[List[str], None]:
        filename = os.path.basename(file_path)

        if not os.path.exists(file_path):
            logger.error(f"File \"{filename}\" does not exist")
            return None

        try:
            with open(file_path, "r") as file:
                data = file.read().splitlines()
                return data

        except Exception as e:
            logger.error(f"Error while reading file \"{file_path}\": {e}")
            logger.exception(e)
            return None

    @staticmethod
    def get_wallets_from_files():
        stark_wallets_data = FileManager.read_data_from_txt_file(paths.STARK_WALLETS_FILE)
        evm_addresses_data = FileManager.read_data_from_txt_file(paths.EVM_ADDRESSES_FILE)
        proxy_data = FileManager.read_data_from_txt_file(paths.PROXY_FILE)
        return WalletManager.get_wallets(aptos_wallets_data=stark_wallets_data,
                                         evm_addresses_data=evm_addresses_data,
                                         proxy_data=proxy_data)

    @staticmethod
    def write_data_to_json_file(file_path: str, data: Union[dict, list]) -> None:
        try:
            with open(file_path, "w") as file:
                json.dump(data, file, indent=4)

        except Exception as e:
            logger.error(f"Error while writing file \"{file_path}\": {e}")
            logger.exception(e)
