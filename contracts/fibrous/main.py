from src.paths import FibrousDir
from utils.file_manager import FileManager


class FibrousContracts:
    def __init__(self):
        self.router_address = '0x00f6f4CF62E3C010E0aC2451cC7807b5eEc19a40b0FaaCd00CCA3914280FDf5a'
        self.router_abi = FileManager.read_abi_from_file(FibrousDir.ROUTER_ABI_FILE)