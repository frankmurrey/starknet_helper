def get_amount_in_from_reserves(amount_out: int,
                                reserve_x: int,
                                reserve_y: int):
    amount_in_with_fee = amount_out * 10000

    numerator = amount_in_with_fee * int(reserve_y)
    denominator = int(reserve_x) * 10000 + amount_in_with_fee

    amount_in = numerator // denominator

    return amount_in


def calculate_price_impact(reserve_in,
                           amount_in):
    return amount_in / (reserve_in + amount_in)


def calc_output_burn_liquidity(reserve_x,
                               reserve_y,
                               lp_supply,
                               to_burn) -> tuple:
    x_return = to_burn * reserve_x / lp_supply
    y_return = to_burn * reserve_y / lp_supply

    return x_return, y_return