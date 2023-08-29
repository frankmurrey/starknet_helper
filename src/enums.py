from enum import Enum


class ModuleName(str, Enum):
    JEDI_SWAP = "jediswap_swap"
    MY_SWAP = "myswap_swap"


class PrivateKeyType(Enum):
    argent = "argent"
    braavos = "braavos"
