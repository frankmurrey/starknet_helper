from typing import Union, List

from src.schemas.wallet_data import WalletData

from utlis.proxy import parse_proxy_data
import config


class WalletManager:

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

            proxy_data = parse_proxy_data(proxy_data=paired_proxy_data)
            wallet_data = WalletData(private_key=private_key,
                                     evm_pair_address=evm_pair_address,
                                     proxy=proxy_data)

            all_wallets.append(wallet_data)

        return all_wallets
