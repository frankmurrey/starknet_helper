from src.paths import StarkVerseDir
from utils.file_manager import FileManager


class StarkVerseContracts:
    def __init__(self):
        self.router_address = '0x060582df2cd4ad2c988b11fdede5c43f56a432e895df255ccd1af129160044b8'
        self.router_abi = FileManager.read_abi_from_file(StarkVerseDir.ROUTER_ABI_FILE)