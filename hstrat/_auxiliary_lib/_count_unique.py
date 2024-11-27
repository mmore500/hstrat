import numpy as np

from ._jit import jit


@jit(nopython=True)
def count_unique(array: np.ndarray) -> int:
    """How many unique values are contained in `array`?"""
    unique_values = set(array)
    return len(unique_values)
