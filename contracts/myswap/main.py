from src.paths import MySwapDir
from utils.file_manager import FileManager


class MySwapContracts:
    def __init__(self):
        self.router_address = '0x010884171baf1914edc28d7afb619b40a4051cfae78a094a55d230f19e944a28'
        self.router_abi = FileManager.read_abi_from_file(MySwapDir.ROUTER_ABI_FILE)