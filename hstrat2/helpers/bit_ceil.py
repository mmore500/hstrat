
def bit_ceil(n: int) -> int:
    """Calculate the smallest power of 2 not smaller than n."""

    if n:
        # see https://stackoverflow.com/a/14267825/17332200
        exp = (n - 1).bit_length()
        res = 1 << exp
        return res
    else:
        return 1
