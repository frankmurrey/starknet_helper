from pydantic import BaseModel
from typing import Optional, Union

from src import enums


class ModuleExecutionResult(BaseModel):
    execution_status: bool = False
    execution_info: Optional[str] = None
    hash: Optional[str] = None

