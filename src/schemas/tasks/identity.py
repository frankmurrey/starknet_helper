from typing import Callable

from pydantic import Field

from src.schemas.tasks.base import TaskBase
from modules.starknet_id.identity_mint import IdentityMint
from src import enums


class IdentityMintTask(TaskBase):
    module_name: enums.ModuleName = enums.ModuleName.IDENTITY
    module_type: enums.ModuleType = enums.ModuleType.MINT
    module: Callable = Field(default=IdentityMint)
