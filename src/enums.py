from enum import Enum


class ModuleType(str, Enum):
    SWAP = "swap"
    MINT = 'mint'
    SUPPLY = 'supply'
    BORROW = 'borrow'
    WITHDRAW = 'withdraw'
    LIQUIDITY_ADD = "liquidity_add"
    LIQUIDITY_REMOVE = "liquidity_remove"
    SEND_MAIL = 'send_mail'


class ModuleName(str, Enum):
    JEDI_SWAP = "jediswap"
    MY_SWAP = "myswap"
    DEPLOY = "deploy"
    DMAIL = 'dmail'
    IDENTITY = 'identity'
    K10SWAP = 'k10swap'
    SITHSWAP = 'sithswap'
    AVNU = 'avnu'
    ZKLEND = 'zklend'


class PrivateKeyType(Enum):
    argent = "argent"
    braavos = "braavos"
