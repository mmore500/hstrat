import typing


def zip_strict(*iterables: typing.Iterable) -> typing.Iterator[typing.Tuple]:
    """Wrapper for zip with strict=True, added in Python 3.10."""
    yield from zip(*iterables, strict=True)
