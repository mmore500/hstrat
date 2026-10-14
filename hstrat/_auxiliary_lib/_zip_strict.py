import itertools as it
import sys
import typing

_sentinel = object()


# adapted from https://docs.python.org/3/library/itertools.html
def zip_strict(*iterables: typing.Iterable) -> typing.Iterator[typing.Tuple]:
    """Polyfill for strict option on zip added in Python 3.10."""
    if sys.version_info >= (3, 10):
        yield from zip(*iterables, strict=True)
    else:
        for combo in it.zip_longest(*iterables, fillvalue=_sentinel):
            if any(sentinel is _sentinel for sentinel in combo):
                raise ValueError
            yield combo
