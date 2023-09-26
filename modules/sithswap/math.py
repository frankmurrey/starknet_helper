def get_amount_in_from_reserves(
        amount_out: int,
        reserve_x: int,
        reserve_y: int
) -> int:
    """
    Get amount in from reserves
    :param amount_out:
    :param reserve_x:
    :param reserve_y:
    :return:
    """
    amount_in_with_fee = amount_out * 10000

    numerator = amount_in_with_fee * int(reserve_y)
    denominator = int(reserve_x) * 10000 + amount_in_with_fee

    amount_in = numerator // denominator

    return amount_in


def calculate_price_impact(
        reserve_in: int,
        amount_in: int,
) -> int:
    """
    Calculate price impact
    :param reserve_in:
    :param amount_in:
    :return:
    """
    return amount_in // (reserve_in + amount_in)


def calc_output_burn_liquidity(
        reserve_x: int,
        reserve_y: int,
        lp_supply: int,
        to_burn: int
) -> tuple:
    """
    Calculate output burn liquidity
    :param reserve_x:
    :param reserve_y:
    :param lp_supply:
    :param to_burn:
    :return:
    """
    x_return = to_burn * reserve_x / lp_supply
    y_return = to_burn * reserve_y / lp_supply

    return x_return, y_return
