from src.paths import UnframedDir
from utils.file_manager import FileManager


class UnframedContracts:
    def __init__(self):
        self.router_address = '0x051734077ba7baf5765896c56ce10b389d80cdcee8622e23c0556fb49e82df1b'
        self.router_abi = FileManager.read_abi_from_file(UnframedDir.ROUTER_ABI_FILE)
