import itertools as it
import typing


# adapted from https://docs.python.org/3/library/itertools.html
def pairwise(iterable: typing.Iterable) -> typing.Iterator:
    """Return successive overlapping pairs taken from the input iterable.

    The number of 2-tuples in the output iterator will be one fewer than the
    number of inputs. It will be empty if the input iterable has fewer than two
    values.
    """
    # pairwise('ABCDEFG') --> AB BC CD DE EF FG
    a, b = it.tee(iterable)
    next(b, None)
    return zip(a, b)


# use library implementation if available (Python 3.10+)
try:
    pairwise = it.pairwise  # noqa: F811
except AttributeError:
    pass
