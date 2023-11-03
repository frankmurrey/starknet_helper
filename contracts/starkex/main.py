from src.paths import StarkExDir
from utils.file_manager import FileManager


class StarkExContracts:
    def __init__(self):
        self.router_address = '0x07ebd0e95dfc4411045f9424d45a0f132d3e40642c38fdfe0febacf78cc95e76'
        self.router_abi = FileManager.read_abi_from_file(StarkExDir.ROUTER_ABI_FILE)
