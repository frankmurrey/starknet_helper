from typing import Union

from pydantic import validator

from src.schemas.configs import validation_mixins
from src.schemas.configs.transaction_settings_base.base import TransactionSettingsBase
from src.exceptions import ModuleConfigValidationError
from utlis import validation
from src import enums


class AddLiquiditySettingsBase(
    TransactionSettingsBase,
    validation_mixins.SlippageValidationMixin,
    validation_mixins.SameCoinValidationMixin
):
    coin_x: Union[str]
    coin_y: Union[str]

    min_amount_out_x: Union[float] = 0
    max_amount_out_x: Union[float] = 0

    use_all_balance_x: Union[bool] = False
    send_percent_balance_x: Union[bool] = False

    slippage: Union[float] = 0.5

    @validator("min_amount_out_x", pre=True)
    def validate_min_amount_out_x_pre(cls, value):
        value = validation.get_converted_to_float(value, "Min Amount Out X")
        value = validation.get_positive(value, "Min Amount Out X", include_zero=False)

        return value

    @validator("max_amount_out_x", pre=True)
    def validate_max_amount_out_x_pre(cls, value, values):
        value = validation.get_converted_to_float(value, "Max Amount Out X")
        value = validation.get_positive(value, "Max Amount Out X", include_zero=False)
        value = validation.get_greater(value, values["min_amount_out_x"], "Max Amount Out X")

        return value


if __name__ == '__main__':
    from loguru import logger
    from pydantic import ValidationError

    try:

        csb = AddLiquiditySettingsBase(
            module_type=enums.ModuleType.SWAP,
            module_name=enums.ModuleName.MY_SWAP,

            max_fee=1,
            forced_gas_limit=False,
            wait_for_receipt=False,
            txn_wait_timeout_sec=60,

            min_delay_sec=0,
            max_delay_sec=1,

            coin_x="ETH",
            coin_y="WETH",

            min_amount_out_x=1,
            max_amount_out_x=1,

            use_all_balance_x=False,
            send_percent_balance_x=False,
            slippage=101
        )

        print(csb.max_fee)

    except ValidationError as e:
        for error in e.errors():
            error_message = error["msg"]
            logger.error(error_message)
        #
        # logger.error(e.errors())
        # print(e.code)
