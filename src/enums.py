from enum import Enum


class ModuleType(str, Enum):
    SWAP = "swap"
    MINT = 'mint'
    SUPPLY = 'supply'
    BORROW = 'borrow'
    WITHDRAW = 'withdraw'
    LIQUIDITY_ADD = "liq_add"
    LIQUIDITY_REMOVE = "liq_remove"
    SEND_MAIL = 'send_mail'
    TEST = 'test'


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
    TEST = 'test'


class PrivateKeyType(str, Enum):
    argent = "argent"
    braavos = "braavos"
