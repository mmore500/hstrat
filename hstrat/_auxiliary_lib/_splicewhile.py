import collections
import itertools as it
import typing

from ._consume import consume


# adapted from https://stackoverflow.com/a/11443871/17332200
def splicewhile(
    predicate: typing.Callable, iterator: typing.Iterator
) -> typing.Tuple[typing.List, typing.Iterator]:
    """Create list of iterator items before predicate is false, consuming them
    from the iterator."""

    if not isinstance(iterator, collections.abc.Iterator):
        # consume is only effectual on an iterator, not an iterable
        # enforce against misconceived usage
        raise TypeError

    it1, it2 = it.tee(iterator)
    res = [*it.takewhile(predicate, it1)]
    consume(it2, len(res))
    return res, it2
