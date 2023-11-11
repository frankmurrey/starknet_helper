from typing import Union
from src import enums

from loguru import logger
from pydantic import BaseModel


class WalletActionSchema(BaseModel):
    module_name: enums.ModuleName = None
    module_type: enums.ModuleType = None

    date_time: str = None
    wallet_address: str = None
    proxy: Union[str, None] = None
    is_success: Union[bool, None] = None
    transaction_hash: str = None

    status: str = None
    traceback: str = None

    def set_error(self, message: str):
        logger.error(message)
        self.status = message
        self.is_success = False
