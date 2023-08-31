from enum import Enum


class ModuleType(Enum):
    SWAP = "swap"
    LIQUIDITY_ADD = "liquidity_add"
    LIQUIDITY_REMOVE = "liquidity_remove"


class ModuleName(str, Enum):
    JEDI_SWAP = "jediswap"
    MY_SWAP = "myswap"
    DEPLOY_ARGENT = "deploy_argent"
    DEPLOY_BRAAVOS = "deploy_braavos"


class PrivateKeyType(Enum):
    argent = "argent"
    braavos = "braavos"
