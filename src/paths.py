import pathlib
import os

MAIN_DIR = os.path.join(pathlib.Path(__file__).parent.parent.resolve())

CONTRACTS_DIR = os.path.join(MAIN_DIR, "contracts")
TOKENS_DIR = os.path.join(CONTRACTS_DIR, "tokens")
TOKENS_ABI_DIR = os.path.join(TOKENS_DIR, "abis")

APP_CONFIG_FILE = os.path.join(MAIN_DIR, "app_config.json")
STARK_WALLETS_FILE = os.path.join(MAIN_DIR, "stark.txt")
EVM_ADDRESSES_FILE = os.path.join(MAIN_DIR, "evm_addresses.txt")
PROXY_FILE = os.path.join(MAIN_DIR, "proxy.txt")


class JediSwapDir:
    _MAIN_DIR = os.path.join(CONTRACTS_DIR, "jediswap")
    ROUTER_ABI_FILE = os.path.join(_MAIN_DIR, "router.abi")


class MySwapDir:
    _MAIN_DIR = os.path.join(CONTRACTS_DIR, "myswap")
    ROUTER_ABI_FILE = os.path.join(_MAIN_DIR, "router.abi")


class StarknetIdDir:
    _MAIN_DIR = os.path.join(CONTRACTS_DIR, "starknet_id")
    ROUTER_ABI_FILE = os.path.join(_MAIN_DIR, "router.abi")


class K10SwapDir:
    _MAIN_DIR = os.path.join(CONTRACTS_DIR, "k10swap")
    ROUTER_ABI_FILE = os.path.join(_MAIN_DIR, "router.abi")


class SithSwapDir:
    _MAIN_DIR = os.path.join(CONTRACTS_DIR, "sithswap")
    ROUTER_ABI_FILE = os.path.join(_MAIN_DIR, "router.abi")


class DmailDir:
    _MAIN_DIR = os.path.join(CONTRACTS_DIR, "dmail")
    ROUTER_ABI_FILE = os.path.join(_MAIN_DIR, "router.abi")


class AvnuDir:
    _MAIN_DIR = os.path.join(CONTRACTS_DIR, "avnu")
    ROUTER_ABI_FILE = os.path.join(_MAIN_DIR, "router.abi")


class ZkLendDir:
    _MAIN_DIR = os.path.join(CONTRACTS_DIR, "zklend")
    ROUTER_ABI_FILE = os.path.join(_MAIN_DIR, "router.abi")


class TempFiles:
    def __init__(self):
        self.TOKENS_JSON_FILE = os.path.join(CONTRACTS_DIR, "tokens.json")
