from src.paths import K10SwapDir
from utlis.file_manager import FileManager


class K10SwapContracts:
    def __init__(self):
        self.router_address = '0x07a6f98c03379b9513ca84cca1373ff452a7462a3b61598f0af5bb27ad7f76d1'
        self.router_abi = FileManager.read_abi_from_file(K10SwapDir.ROUTER_ABI_FILE)