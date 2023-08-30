from typing import List

from eth_account import Account

from utlis.key_manager.key_manager import get_argent_key_from_phrase
from utlis.key_manager.key_manager import get_braavos_key_from_phrase


class Generator:

    @staticmethod
    def generate_mnemonics(
            amount: int
    ) -> List[str]:
        """
        Generate a list of mnemonics.

        Args:
            amount (int): The amount of mnemonics to generate.

        Returns:
            List[str]: A list of mnemonics.

        """
        Account.enable_unaudited_hdwallet_features()
        mnemonics = []
        for _ in range(amount):
            mnemonics.append(Account.create_with_mnemonic()[1])

        return mnemonics

    @staticmethod
    def extract_argent_keys_from_mnemonics(
            mnemonics: List[str]) -> List[str]:
        """
        Extracts argent keys from mnemonics.

        Args:
            mnemonics (List[str]): A list of mnemonics.

        Returns:
            List[str]: A list of argent keys.
        """

        keys = []
        for mnemonic in mnemonics:
            keys.append(get_argent_key_from_phrase(mnemonic))

        return keys

    @staticmethod
    def extract_braavos_keys_from_mnemonics(
            mnemonics: List[str]) -> List[str]:
        """
        Extracts braavos keys from mnemonics.

        Args:
            mnemonics (List[str]): A list of mnemonics.

        Returns:
            List[str]: A list of braavos keys.
        """

        keys = []
        for mnemonic in mnemonics:
            keys.append(get_braavos_key_from_phrase(mnemonic))

        return keys
