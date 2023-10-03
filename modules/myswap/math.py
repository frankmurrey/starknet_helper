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
        amount_in: int
) -> int:
    return amount_in // (reserve_in + amount_in)


def calc_output_burn_liquidity(
        reserve_x: int,
        reserve_y: int,
        lp_supply: int,
        to_burn: int
) -> tuple:
    x_return = to_burn * reserve_x // lp_supply
    y_return = to_burn * reserve_y // lp_supply

    return x_return, y_return


if __name__ == '__main__':
    amt_out = 100000
    res_x = 614114447961
    resy = 581493852783
    out = get_amount_in_from_reserves(amount_out=amt_out,
                                      reserve_x=res_x,
                                      reserve_y=resy)
    print(out)

    lp_res_x = 615837552064
    lp_res_y = 579770161207
    to_burn = 88858
    lp_supply = 360596804969

    x, y = calc_output_burn_liquidity(reserve_x=lp_res_x,
                                      reserve_y=lp_res_y,
                                      lp_supply=lp_supply,
                                      to_burn=to_burn)
