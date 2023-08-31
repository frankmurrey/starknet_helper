from src.paths import K10SwapDir
from utlis.file_manager import FileManager


class JediSwapContracts:
    def __init__(self):
        self.router_address = '0x041fd22b238fa21cfcf5dd45a8548974d8263b3a531a60388411c5e230f97023'
        self.router_abi = FileManager.read_abi_from_file(K10SwapDir.ROUTER_ABI_FILE)