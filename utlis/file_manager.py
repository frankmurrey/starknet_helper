import os
import json
from typing import Union, List

from src import paths
from src.schemas.proxy_data import ProxyData
from src.schemas.wallet_data import WalletData

import config


class FileManager:

    def __init__(self):
        pass

    @staticmethod
    def read_abi_from_file(file_path: str):
        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, "r") as f:
                return json.loads(f.read())
        except Exception as e:
            return None

    @staticmethod
    def read_data_from_json_file(file_path):
        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, "r") as file:
                data = json.load(file)
                return data

        except Exception as e:
            return None

    @staticmethod
    def read_data_from_txt_file(file_path) -> Union[list, None]:
        if not os.path.exists(file_path):
            return None

        with open(file_path, "r") as file:
            data = file.read().splitlines()
            return data

    @staticmethod
    def _extract_valid_proxy_data_from_str(proxy_data: str) -> Union[List[ProxyData], None]:
        if not proxy_data:
            return None

        if proxy_data == "##":
            return None

        try:
            if proxy_data.startswith('m$'):
                is_mobile = True
                proxy_data = proxy_data[2:]
            else:
                is_mobile = False

            proxy_data = proxy_data.split(":")
            if len(proxy_data) == 2:
                host, port = proxy_data
                proxy_data = ProxyData(host=host,
                                       port=port,
                                       is_mobile=is_mobile)

            elif len(proxy_data) == 4:
                host, port, username, password = proxy_data
                proxy_data = ProxyData(host=host,
                                       port=port,
                                       username=username,
                                       password=password,
                                       auth=True,
                                       is_mobile=is_mobile)

            else:
                proxy_data = None

            return proxy_data
        except Exception as e:
            return None

    @staticmethod
    def get_wallets(aptos_wallets_data=None,
                    evm_addresses_data=None,
                    proxy_data=None) -> Union[List[WalletData], None]:

        if not aptos_wallets_data:
            return None
        all_evm_addresses = []
        if evm_addresses_data:
            all_evm_addresses = [addr for addr in evm_addresses_data if len(addr) == config.EVM_ADDRESS_LENGTH]

        all_proxy_data = []
        if proxy_data:
            all_proxy_data = [proxy for proxy in proxy_data]

        all_wallets = []
        for index, private_key in enumerate(aptos_wallets_data):
            evm_pair_address = all_evm_addresses[index] if len(all_evm_addresses) > index else None
            paired_proxy_data = all_proxy_data[index] if len(all_proxy_data) > index else None
            if len(private_key) != config.STARK_KEY_LENGTH:
                continue
            proxy_data = FileManager._extract_valid_proxy_data_from_str(paired_proxy_data)
            wallet_data = WalletData(private_key=private_key,
                                     evm_pair_address=evm_pair_address,
                                     proxy=proxy_data)
            all_wallets.append(wallet_data)

        return all_wallets

    @staticmethod
    def get_wallets_from_files():
        stark_wallets_data = FileManager.read_data_from_txt_file(paths.STARK_WALLETS_FILE)
        evm_addresses_data = FileManager.read_data_from_txt_file(paths.EVM_ADDRESSES_FILE)
        proxy_data = FileManager.read_data_from_txt_file(paths.PROXY_FILE)
        return FileManager.get_wallets(aptos_wallets_data=stark_wallets_data,
                                       evm_addresses_data=evm_addresses_data,
                                       proxy_data=proxy_data)
