import numpy as np

from ._jit import jit


@jit(nopython=True)
def count_unique(array: np.array) -> np.array:
    """How many unique values are contained `array`?"""
    unique_values = set(array)
    return len(unique_values)
