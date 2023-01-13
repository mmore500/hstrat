import sys
import typing

import more_itertools as mit


# adapted from https://docs.python.org/3/library/itertools.html
def zip_strict(*iterables: typing.Iterable) -> typing.Iterator[typing.Tuple]:
    """Polyfill for strict option on zip added in Python 3.10."""
    if sys.version_info >= (3, 10):
        yield from zip(*iterables, strict=True)
    elif len(iterables):
        try:
            yield from mit.zip_equal(*iterables)
        except mit.UnequalIterablesError:
            raise ValueError
    else:
        yield from zip()
