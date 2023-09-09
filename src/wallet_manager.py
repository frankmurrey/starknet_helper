from typing import Union, List, Dict, Any

from src.schemas.wallet_data import WalletData

import config


class WalletManager:

    @staticmethod
    def get_wallets(wallets_data: List[Dict[str, Any]]):
        wallets = [
            WalletData(**wallet_item)
            for wallet_item in wallets_data
        ]
        return wallets
