import numbers
import typing

from ._pairwise import pairwise


def is_nondecreasing(
    seq: typing.Iterable, *, atol: numbers.Number = 0
) -> bool:
    """Is each element no less than the one before it, allowing decreases of
    at most `atol`?"""
    return all(a <= b + atol for a, b in pairwise(seq))
