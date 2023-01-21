import numba as nb
import numpy as np


@nb.jit(nopython=True)
def count_unique(array: np.array) -> np.array:
    unique_values = set(array)
    return len(unique_values)
