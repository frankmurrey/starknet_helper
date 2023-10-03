from src.paths import DmailDir
from utils.file_manager import FileManager


class DmailContracts:
    def __init__(self):
        self.router_address = '0x0454f0bd015e730e5adbb4f080b075fdbf55654ff41ee336203aa2e1ac4d4309'
        self.router_abi = FileManager.read_abi_from_file(DmailDir.ROUTER_ABI_FILE)
