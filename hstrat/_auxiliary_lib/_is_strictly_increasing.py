import typing

from ._pairwise import pairwise


def is_strictly_increasing(seq: typing.Iterable) -> bool:

    return all(a < b for a, b in pairwise(seq))
