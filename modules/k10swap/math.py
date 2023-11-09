from typing import Tuple
from decimal import Decimal, getcontext

getcontext().prec = 100

ZERO = Decimal('0')
FIVE = Decimal('5')


def sqrt(x):
    """ Compute the square root of x, where x is a Decimal. """
    return x.sqrt()


def get_total_supply_adjusted(
        total_supply: int,
        reserves: Tuple[int, int],
        fee_on: bool,
        k_last: int
) -> Decimal:
    total_supply_adjusted = Decimal(total_supply)
    reserve0, reserve1 = map(Decimal, reserves)
    k_last_parsed = Decimal(k_last)

    if fee_on and k_last_parsed != ZERO:
        root_k = sqrt(reserve0 * reserve1)
        root_k_last = sqrt(k_last_parsed)

        if root_k > root_k_last:
            numerator = (total_supply_adjusted * (root_k - root_k_last))
            denominator = (root_k * FIVE) + root_k_last
            fee_liquidity = numerator / denominator
            total_supply_adjusted += fee_liquidity

    return total_supply_adjusted


def get_liquidity_value(
        total_supply: int,
        liquidity: int,
        reserve_x: int,
        reserve_y: int,
) -> Tuple[Decimal, Decimal]:

    fee_on = True
    k_last = 0
    reserves = (reserve_x, reserve_y)

    total_supply_adjusted = get_total_supply_adjusted(total_supply, reserves, fee_on, k_last)
    liquidity_decimal = Decimal(liquidity)
    reserve0, reserve1 = map(Decimal, reserves)

    return (
        (liquidity_decimal * reserve0) / total_supply_adjusted,
        (liquidity_decimal * reserve1) / total_supply_adjusted
    )


if __name__ == '__main__':
    value = get_liquidity_value(
        186211007755,
        8638335,
        214924212999,
        214439085890
    )
    print(value)

