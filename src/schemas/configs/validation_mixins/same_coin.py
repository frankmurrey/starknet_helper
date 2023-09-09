from pydantic import BaseModel
from pydantic import validator

from src.exceptions import ModuleConfigValidationError


class SameCoinValidationMixin(BaseModel):

    @validator("coin_y", pre=True, check_fields=False)
    def validate_coin_y_pre(cls, value, values):

        if value == values["coin_x"]:
            raise ModuleConfigValidationError("Coin Y cannot be the same as Coin X")

        return value
