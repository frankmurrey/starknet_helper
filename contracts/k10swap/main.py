from src.paths import K10SwapDir
from utils.file_manager import FileManager


class K10SwapContracts:
    def __init__(self):
        self.router_address = '0x07a6f98c03379b9513ca84cca1373ff452a7462a3b61598f0af5bb27ad7f76d1'
        self.router_abi = FileManager.read_abi_from_file(K10SwapDir.ROUTER_ABI_FILE)

        self.factory_address = '0x1c0a36e26a8f822e0d81f20a5a562b16a8f8a3dfd99801367dd2aea8f1a87a2'
        self.factory_abi = FileManager.read_abi_from_file(K10SwapDir.FACTORY_ABI_FILE)

        self.pool_abi = FileManager.read_abi_from_file(K10SwapDir.POOL_ABI_FILE)
