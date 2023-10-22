from src.paths import OrbiterDir
from utils.file_manager import FileManager


class OrbiterContracts:
    def __init__(self):
        self.router_address = '0x0173f81c529191726c6e7287e24626fe24760ac44dae2a1f7e02080230f8458b'
        self.router_abi = FileManager.read_abi_from_file(OrbiterDir.ROUTER_ABI_FILE)
