from src.paths import ZkLendDir
from utils.file_manager import FileManager


class ZkLendContracts:
    def __init__(self):
        self.router_address = '0x04c0a5193d58f74fbace4b74dcf65481e734ed1714121bdc571da345540efa05'
        self.router_abi = FileManager.read_abi_from_file(ZkLendDir.ROUTER_ABI_FILE)
