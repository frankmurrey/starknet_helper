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


if __name__ == '__main__':
    amt_out = int(1e13)
    res_x = 329114913443
    resy = 327959969505
    out = get_amount_in_from_reserves(amount_out=amt_out,
                                      reserve_x=res_x,
                                      reserve_y=resy)
    print(calculate_price_impact(reserve_in=res_x,
                                 amount_in=amt_out))
