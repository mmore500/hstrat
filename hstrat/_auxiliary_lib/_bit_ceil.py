def bit_ceil(n: int) -> int:
    """Calculate the smallest power of 2 not smaller than a
    non-negative integer n."""
    assert n >= 0
    if n:
        # see https://stackoverflow.com/a/14267825/17332200
        # cast to int to make robust to numpy.int32, numpy.int64, etc.
        exp = int(n - 1).bit_length()
        res = 1 << exp
        return res
    else:
        return 1
