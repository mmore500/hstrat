import numpy as np

from ._jit import jit


@jit(nopython=True)
def all_unique(array: np.ndarray) -> bool:
    """Are all values in `array` unique?"""
    seen_unique = set()
    for idx, val in enumerate(array):
        seen_unique.add(val)
        if idx + 1 != len(seen_unique):
            return False

    return True
