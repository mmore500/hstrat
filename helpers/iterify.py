import typing


def iterify(*args) -> typing.Iterator[typing.Any]:
    return iter(args)
