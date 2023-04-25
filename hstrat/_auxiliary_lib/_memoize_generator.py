import itertools as it
import typing

import lru


def memoize_generator(lru_cache_size: int = 128) -> typing.Callable:
    """Decorator to memoize a generator function using an LRU cache.

    The cache stores the original generator and a list of its values.
    When the generator is called, if the arguments are in the cache,
    the cached values are returned, otherwise the generator is executed and its values are stored.

    Parameters
    ----------
    lru_cache_size : int, default 128
        The maximum size of the LRU cache.

    Returns
    -------
    callable
        Decorator function to memoize a generator.

    Examples
    --------
    >>> @memoize_generator(lru_cache_size=2)
    ... def gen(n):
    ...     for i in range(n):
    ...         yield i
    ...
    >>> g = gen(3)
    >>> list(g)
    [0, 1, 2]
    >>> g = gen(3)
    >>> list(g)
    [0, 1, 2]
    """
    # adapted from https://stackoverflow.com/a/10726355/17332200
    def decorator(generator: typing.Callable) -> typing.Callable:
        cache_original = lru.LRU(lru_cache_size)
        cache_copy = lru.LRU(lru_cache_size)

        def ret(*args) -> typing.Generator:
            if args not in cache_original:
                cache_original[args] = generator(*args)
                cache_copy[args] = []

            original = cache_original[args]
            copy = cache_copy[args]

            for idx in it.count():
                if idx < len(copy):
                    yield copy[idx]
                else:
                    assert idx == len(copy)
                    try:
                        copy.append(next(original))
                        yield copy[idx]
                    except StopIteration:
                        return

        return ret

    return decorator
