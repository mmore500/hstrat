def bit_floor(n: int) -> int:
    """Calculate the largest power of two not greater than n.

    If zero, returns zero."""

    if n:
        # see https://stackoverflow.com/a/14267825/17332200
        exp = (n // 2).bit_length()
        res = 1 << exp
        return res
    else:
        return 0
