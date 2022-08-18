import itertools as it

import lru


def memoize_generator(lru_cache_size: int=128):

    # adapted from https://stackoverflow.com/a/10726355/17332200
    def decorator(generator):
        cache_original=lru.LRU(lru_cache_size)
        cache_copy=lru.LRU(lru_cache_size)

        def ret(*args):
            if args not in cache_original:
                cache_original[args]=generator(*args)
                cache_copy[args]=[]

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
