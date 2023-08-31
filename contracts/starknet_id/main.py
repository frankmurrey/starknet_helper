from src.paths import StarknetIdDir
from utlis.file_manager import FileManager


class StarkNetIdContracts:
    def __init__(self):
        self.router_address = '0x05dbdedc203e92749e2e746e2d40a768d966bd243df04a6b712e222bc040a9af'
        self.router_abi = FileManager.read_abi_from_file(StarknetIdDir.ROUTER_ABI_FILE)