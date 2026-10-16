import typing


def zip_strict(*iterables: typing.Iterable) -> typing.Iterator[typing.Tuple]:
    """Polyfill for strict option on zip added in Python 3.10."""
    yield from zip(*iterables, strict=True)
