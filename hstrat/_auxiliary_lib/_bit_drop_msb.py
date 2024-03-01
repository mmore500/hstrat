from ._bit_floor import bit_floor


def bit_drop_msb(n: int) -> int:
    """Drop most significant bit from binary representation of integer n."""
    return n & (~bit_floor(n))
