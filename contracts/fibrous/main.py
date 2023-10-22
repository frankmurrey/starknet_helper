from src.paths import FibrousDir
from utils.file_manager import FileManager


class FibrousContracts:
    def __init__(self):
        self.router_address = '0x03201e8057a781dca378564b9d3bbe9b5b7617fac4ad9d9deaa1024cf63f877e'
        self.router_abi = FileManager.read_abi_from_file(FibrousDir.ROUTER_ABI_FILE)