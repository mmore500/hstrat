def bit_floor(n: int) -> int:
    """Calculate the largest power of two not greater than n.

    If zero, returns zero.
    """
    if n:
        # see https://stackoverflow.com/a/14267825/17332200
        # cast to int to make robust to numpy.int32, numpy.int64, etc.
        exp = int(n // 2).bit_length()
        res = 1 << exp
        return res
    else:
        return 0
