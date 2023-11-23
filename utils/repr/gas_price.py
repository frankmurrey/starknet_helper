from typing import Union, Optional


def gas_price_waiting_msg(
    target_price_wei: Union[int, float],
    current_gas_price: Union[int, float],
    is_timeout_needed: bool = False,
    time_out_sec: Union[int, float] = None,
) -> str:
    """
    Get message string for gas price waiting
    Args:
        target_price_wei: Target gas price (wei)
        current_gas_price: Current gas price
        is_timeout_needed: Is timeout needed
        time_out_sec: Time out (sec)

    Returns: message string for gas price waiting
    """
    msg = f"Waiting for gas price to be lower than {target_price_wei / 10 ** 9} Gwei. " \
          f"(Current - {round(current_gas_price / 10 ** 9, 2)} Gwei)"

    if is_timeout_needed:
        msg += f" | Timeout: {time_out_sec} sec."

    return msg
