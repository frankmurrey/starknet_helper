from src.paths import ZeriusDir
from utils.file_manager import FileManager


class ZeriusContracts:
    def __init__(self):
        self.router_address = '0x043ba5e69eec55ce374e1ce446d16ee4223c1ba48c808d2dcd4e606f94ec9e15'
        self.router_abi = FileManager.read_abi_from_file(ZeriusDir.ROUTER_ABI_FILE)

