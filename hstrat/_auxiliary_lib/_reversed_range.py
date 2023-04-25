import typing


def reversed_range(
    start: int, stop: typing.Optional[int] = None
) -> typing.Iterator[int]:
    """Iterate through a range in reverse order.

    Equivalent to `reversed(range(*args))`. Compatible with numba jit.
    """
    # numba jit doesn't support yield from or reversed
    cur = stop if stop is not None else start
    last = start if stop is not None else 0
    while cur > last:
        cur -= 1
        yield cur
