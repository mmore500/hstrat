import numpy as np

from ._jit_if_has_numba import jit_if_has_numba


@jit_if_has_numba(nopython=True)
def count_unique(array: np.array) -> np.array:
    unique_values = set(array)
    return len(unique_values)
