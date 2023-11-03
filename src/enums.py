from enum import Enum


class ModuleType(str, Enum):
    DEPLOY = "deploy"
    UPGRADE = "upgrade"
    SWAP = "swap"
    MINT = "mint"
    SUPPLY = "supply"
    BORROW = "borrow"
    WITHDRAW = "withdraw"
    LIQUIDITY_ADD = "liq_add"
    LIQUIDITY_REMOVE = "liq_remove"
    SEND_MAIL = "send_mail"
    TEST = "test"
    SEND = "send"
    BRIDGE = "bridge"
    TRANSFER = "transfer"


class ModuleName(str, Enum):
    JEDI_SWAP = "jediswap"
    MY_SWAP = "myswap"
    DMAIL = "dmail"
    IDENTITY = "starkid"
    K10SWAP = "k10swap"
    SITHSWAP = "sithswap"
    AVNU = "avnu"
    ZKLEND = "zklend"
    TEST = "test"
    DEPLOY = "deploy"
    UPGRADE = "upgrade"
    TRANSFER = "transfer"
    RANDOM = "random"
    FIBROUS = "fibrous"
    ORBITER = "orbiter"
    STARK_BRIDGE = "starkgate"
    STARK_VERSE = "starkverse"


class TabName(str, Enum):
    SWAP = "Swap"
    ADD_LIQUIDITY = "Add Liquidity"
    REMOVE_LIQUIDITY = "Remove Liquidity"
    SUPPLY_LENDING = "Supply Lending"
    WITHDRAW_LENDING = "Withdraw Lending"
    MINT = "Mint"
    DMAIL_SEND_MAIL = "Dmail Send Mail"
    DEPLOY = "Deploy"
    UPGRADE = "Upgrade"
    TRANSFER = "Transfer"
    BRIDGE = "Bridge"


class PrivateKeyType(str, Enum):
    argent = "argent"
    braavos = "braavos"


class TaskStatus(str, Enum):
    CREATED = "created"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"


class WalletStatus(str, Enum):
    active = "active"
    completed = "completed"
    inactive = "inactive"


class MiscTypes(str, Enum):
    RANDOM = "random"


class BlockStatus(str, Enum):
    PENDING = "pending"
    LATEST = "latest"
