from typing import Optional, List

from pydantic import BaseModel
from starknet_py.net.client_models import Call


class ModuleExecutionResult(BaseModel):
    execution_status: bool = False
    retry_needed: bool = True
    execution_info: Optional[str] = None
    hash: Optional[str] = None


class TransactionPayloadData(BaseModel):
    calls: List[Call]
    amount_x_decimals: float
    amount_y_decimals: float

