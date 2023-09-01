from src.paths import AvnuDir
from utlis.file_manager import FileManager


class AvnuContracts:
    def __init__(self):
        self.router_address = '0x04270219d365d6b017231b52e92b3fb5d7c8378b05e9abc97724537a80e93b0f'
        self.router_abi = FileManager.read_abi_from_file(AvnuDir.ROUTER_ABI_FILE)