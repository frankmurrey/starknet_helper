from typing import Optional, List

from pydantic import BaseModel
from starknet_py.net.client_models import Call


class ModuleExecutionResult(BaseModel):
    execution_status: bool = False
    execution_info: Optional[str] = ""
    retry_needed: bool = True
    hash: Optional[str] = ""


class TransactionPayloadData(BaseModel):
    calls: List[Call]
    amount_x_decimals: float
    amount_y_decimals: float

