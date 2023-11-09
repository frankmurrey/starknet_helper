from typing import Callable
from pydantic import Field

from modules.starkverse.mint import PublicMint
from src.schemas.tasks.base.mint import MintTaskBase
from src import enums


class StarkVersePublicMintTask(MintTaskBase):
    module_type = enums.ModuleType.MINT
    module_name = enums.ModuleName.STARK_VERSE
    module: Callable = Field(default=PublicMint)
