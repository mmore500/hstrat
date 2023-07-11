def count_trailing_zeros(n: int) -> int:
    """Count the number of trailing zeros in the binary representation of the
    absolute value of an integer.

    Trailing zeros are contiguous unset bits before the first set bit at the
    least significant (rightmost) position. For example, the number 8
    (1000 in binary) has 3 trailing zeros. Returns 0 trailing bits for 0.

    Examples
    --------
    >>> count_trailing_zeros(8)
    3

    >>> count_trailing_zeros(0)
    0
    """
    return (n & -n).bit_length() - 1 if n else 0
