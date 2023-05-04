import collections
import itertools as it
import typing


# adapted from https://docs.python.org/3/library/itertools.html
def consume(iterator: typing.Iterator, n: int = None) -> None:
    "Advance the iterator n-steps ahead. If n is None, consume entirely."

    if not isinstance(iterator, collections.abc.Iterator):
        # consume is only effectual on an iterator, not an iterable
        # enforce against misconceived usage
        raise TypeError

    # Use functions that consume iterators at C speed.
    if n is None:
        # feed the entire iterator into a zero-length deque
        collections.deque(iterator, maxlen=0)
    else:
        # advance to the empty slice starting at position n
        next(it.islice(iterator, n, n), None)
