import typing

from ._pairwise import pairwise


def omit_last(it: typing.Iterable) -> typing.Iterable:
    for first, __ in pairwise(it):
        yield first
