import pathlib
import os

MAIN_DIR = os.path.join(pathlib.Path(__file__).parent.parent.resolve())

CONTRACTS_DIR = os.path.join(MAIN_DIR, "contracts")
TOKENS_DIR = os.path.join(CONTRACTS_DIR, "tokens")
TOKENS_ABI_DIR = os.path.join(TOKENS_DIR, "abis")


class JediSwapDir:
    _MAIN_DIR = os.path.join(CONTRACTS_DIR, "jediswap")
    ROUTER_ABI_FILE = os.path.join(_MAIN_DIR, "router.abi")


class MySwapDir:
    _MAIN_DIR = os.path.join(CONTRACTS_DIR, "myswap")
    ROUTER_ABI_FILE = os.path.join(_MAIN_DIR, "router.abi")


class TempFiles:
    def __init__(self):
        self.TOKENS_JSON_FILE = os.path.join(CONTRACTS_DIR, "tokens.json")
