from pydantic import BaseModel
from pydantic import validator

from utlis import validation


class MinMaxAmountOutValidationMixin(BaseModel):

    @validator("min_amount_out", pre=True, check_fields=False)
    def validate_min_amount_out_pre(cls, value):
        value = validation.get_converted_to_float(value, "Min Amount Out")
        value = validation.get_positive(value, "Min Amount Out", include_zero=False)

        return value

    @validator("max_amount_out", pre=True, check_fields=False)
    def validate_max_amount_out_pre(cls, value, values):
        value = validation.get_converted_to_float(value, "Max Amount Out")
        value = validation.get_positive(value, "Max Amount Out", include_zero=False)
        value = validation.get_greater(value, values["min_amount_out"], "Max Amount Out")

        return value
