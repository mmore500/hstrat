from ._count_trailing_zeros import count_trailing_zeros


def count_trailing_ones(n: int) -> int:
    """Count the number of trailing ones in the binary representation of the
    absolute value of an integer.

    Trailing ones are contiguous set bits before the first unset bit at the least significant (rightmost) position. For example, the number 9 (1001 in binary) has 1 trailing one. Returns 0 trailing bits for 0.

    Examples
    --------
    >>> count_trailing_ones(9)
    1

    >>> count_trailing_ones(0)
    0
    """
    return count_trailing_zeros(~abs(n))
