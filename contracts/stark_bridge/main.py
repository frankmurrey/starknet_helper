from src.paths import StarkBridgeDir
from utils.file_manager import FileManager


class StarkBridgeContracts:
    def __init__(self):
        self.router_address = '0x073314940630fd6dcda0d772d4c972c4e0a9946bef9dabf4ef84eda8ef542b82'
        self.router_abi = FileManager.read_abi_from_file(StarkBridgeDir.ROUTER_ABI_FILE)
