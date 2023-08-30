from enum import Enum


class ModuleName(str, Enum):
    JEDI_SWAP = "jediswap_swap"
    MY_SWAP = "myswap_swap"
    DEPLOY_ARGENT = "deploy_argent"
    DEPLOY_BRAAVOS = "deploy_braavos"


class PrivateKeyType(Enum):
    argent = "argent"
    braavos = "braavos"
