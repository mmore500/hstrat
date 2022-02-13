import itertools as it
import typing


def cyclify(*args) -> typing.Iterator[typing.Any]:
    return it.cycle(args)
