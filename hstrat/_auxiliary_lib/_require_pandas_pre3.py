import functools

from packaging.version import parse as parse_version
import pandas as pd


def require_pandas_pre3(func):
    """Decorator that raises RuntimeError if pandas >= 3.

    Directs users to the phyloframe.legacy equivalent instead.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if parse_version(pd.__version__) >= parse_version("3"):
            raise RuntimeError(
                f"{func.__name__} is not compatible with pandas >= 3. "
                f"Use phyloframe.legacy.{func.__name__} instead.",
            )
        return func(*args, **kwargs)

    return wrapper
