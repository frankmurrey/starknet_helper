from typing import List

from eth_account import Account
from starknet_py.net.signer.stark_curve_signer import KeyPair

from src import enums
from utils.key_manager.key_manager import get_argent_key_from_phrase
from utils.key_manager.key_manager import get_braavos_key_from_phrase
from utils.key_manager.key_manager import get_argent_addr_from_private_key
from utils.key_manager.key_manager import get_braavos_addr_from_private_key


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

    @staticmethod
    def extract_argent_addresses_from_private_keys(
            private_keys: List[str],
            cairo_version: int = 1) -> List[str]:
        """
        Extracts argent addresses from mnemonics.

        Args:
            private_keys (List[str]): A list of private_keys.
            cairo_version (int, optional): The cairo version. Defaults to 1.

        Returns:
            List[str]: A list of argent addresses.
        """

        addresses = []
        for private_key in private_keys:
            addresses.append(
                get_argent_addr_from_private_key(
                    private_key=private_key,
                    cairo_version=cairo_version
                )
            )

        return addresses

    @staticmethod
    def extract_braavos_addresses_from_private_keys(
            private_keys: List[str],
            cairo_version: int = 1) -> List[str]:
        """
        Extracts braavos addresses from mnemonics.

        Args:
            private_keys (List[str]): A list of private_keys.
            cairo_version (int, optional): The cairo version. Defaults to 1.

        Returns:
            List[str]: A list of braavos addresses.
        """

        addresses = []
        for private_key in private_keys:
            addresses.append(
                get_braavos_addr_from_private_key(
                    private_key=private_key,
                    cairo_version=cairo_version
                )
            )

        return addresses

    @staticmethod
    def generate_mnemonics_with_key_pair(
            amount: int,
            wallet_type: enums.PrivateKeyType
    ) -> List[dict]:
        """
        Generate a list of mnemonics with key pairs.

        Args:
            amount (int): The amount of mnemonics to generate.
            wallet_type (enums.PrivateKeyType): The type of the key pair (Argent or Braavos).

        Returns:
            List[tuple[str, str]]: A list of mnemonics with key pairs.

        """
        if wallet_type == enums.PrivateKeyType.argent.value:
            pk_extractor = Generator.extract_argent_keys_from_mnemonics
            address_extractor = Generator.extract_argent_addresses_from_private_keys
        else:
            pk_extractor = Generator.extract_braavos_keys_from_mnemonics
            address_extractor = Generator.extract_braavos_addresses_from_private_keys

        mnemonics = Generator.generate_mnemonics(amount=amount)
        private_keys = pk_extractor(mnemonics=mnemonics)
        addresses = address_extractor(private_keys=private_keys)

        return [
            {
                'mnemonic': mnemonic,
                'private_key': private_key,
                'address': hex(address),
                'public_key': hex(KeyPair.from_private_key(private_key).public_key)
            }
            for mnemonic, private_key, address in zip(mnemonics, private_keys, addresses)
        ]
