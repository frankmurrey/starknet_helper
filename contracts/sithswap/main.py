from src.paths import SithSwapDir
from utlis.file_manager import FileManager


class SithSwapContracts:
    def __init__(self):
        self.router_address = '0x028c858a586fa12123a1ccb337a0a3b369281f91ea00544d0c086524b759f627'
        self.router_abi = FileManager.read_abi_from_file(SithSwapDir.ROUTER_ABI_FILE)
