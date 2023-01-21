import typing

from ._pairwise import pairwise


def omit_last(it: typing.Iterable) -> typing.Iterable:
    """Yield iterable values in order, stopping iteration after second-to-last
    value yielded.

    Conceptually equivalent to `[:-1]` slice.
    """
    for first, __ in pairwise(it):
        yield first
