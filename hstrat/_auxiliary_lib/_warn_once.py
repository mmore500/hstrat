from functools import lru_cache
import warnings


@lru_cache(maxsize=None)
def warn_once(msg: str):
    warnings.warn(msg)
