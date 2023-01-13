import typing

from ._pairwise import pairwise


def is_nonincreasing(seq: typing.Iterable) -> bool:

    return all(a >= b for a, b in pairwise(seq))
