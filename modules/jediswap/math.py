def get_lp_burn_output(
        amount_to_burn: int,
        total_supply: int,
        contract_balance_x: int,
        contract_balance_y: int
) -> tuple:
    """
    Get the amount of tokens to burn from liquidity pool
    :param amount_to_burn:
    :param total_supply:
    :param contract_balance_x:
    :param contract_balance_y:
    :return:
    """

    liquidity_mul_balance_x = amount_to_burn * contract_balance_x
    amount_x = liquidity_mul_balance_x / total_supply

    liquidity_mul_balance_y = amount_to_burn * contract_balance_y
    amount_y = liquidity_mul_balance_y / total_supply

    return int(amount_x), int(amount_y)


if __name__ == '__main__':
    to_burn = 86662
    supply = 656576883708
    balance_x = 755832000000
    balance_y = 755311000000

    am_x, am = get_lp_burn_output(amount_to_burn=to_burn,
                                  total_supply=supply,
                                  contract_balance_x=balance_x,
                                  contract_balance_y=balance_y)