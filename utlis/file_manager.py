import os
import json
from typing import Union, List
from datetime import datetime

from src import paths
from src.wallet_manager import WalletManager

import csv
from loguru import logger


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

    @staticmethod
    def create_new_logs_dir(dir_name_suffix=None):
        if os.path.exists(paths.LOGS_DIR) is False:
            os.mkdir(paths.LOGS_DIR)
            logger.info(f"Creating logs dir in \"{paths.LOGS_DIR}\"")

        date_time = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        if dir_name_suffix:
            dir_name = f"log_{dir_name_suffix}_{date_time}"
        else:
            dir_name = f"log_{date_time}"

        new_logs_dir = f"{paths.LOGS_DIR}\\{dir_name}"
        os.mkdir(new_logs_dir)

        if not os.path.exists(new_logs_dir):
            return
        return new_logs_dir

    @staticmethod
    def write_data_to_csv(path,
                          file_name,
                          data: list):
        if not os.path.exists(path):
            logger.error(f"Path \"{path}\" does not exist")
            return

        file_path = f"{path}\\{file_name}"
        with open(file_path, "a", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)
