from src.paths import FlexDir
from utils.file_manager import FileManager


class FlexContracts:
    def __init__(self):
        self.router_address = '0x04b1b3fdf34d00288a7956e6342fb366a1510a9387d321c87f3301d990ac19d4'
        self.router_abi = FileManager.read_abi_from_file(FlexDir.ROUTER_ABI_FILE)
