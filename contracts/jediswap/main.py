from src.paths import JediSwapDir
from utlis.file_manager import FileManager


class JediSwapContracts:
    def __init__(self):
        self.router_address = '0x041fd22b238fa21cfcf5dd45a8548974d8263b3a531a60388411c5e230f97023'
        self.router_abi = FileManager.read_abi_from_file(JediSwapDir.ROUTER_ABI_FILE)

        self.factory_address = '0x00dad44c139a476c7a17fc8141e6db680e9abc9f56fe249a105094c44382c2fd'
        self.factory_abi = FileManager.read_abi_from_file(JediSwapDir.FACTORY_ABI_FILE)

        self.pool_abi = FileManager.read_abi_from_file(JediSwapDir.POOL_ABI_FILE)
