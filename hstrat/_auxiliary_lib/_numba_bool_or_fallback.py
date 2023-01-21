import typing

import numpy as np


def numba_bool_or_fallback() -> typing.Type:
    """Returns numba bool type or, if numba unavailable, numpy bool type."""
    try:
        import numba as nb
    except ImportError:
        return np.bool_
    else:
        return nb.types.bool_
