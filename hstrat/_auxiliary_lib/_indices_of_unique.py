import numpy as np

from ._jit_if_has_numba import jit_if_has_numba


@jit_if_has_numba(nopython=True)
def indices_of_unique(array: np.array) -> np.array:
    unique_indices = []
    seen_values = set()
    last_value = 0  # if seen_values empty, last_value not compared against
    for index, value in enumerate(array):
        is_same_as_last_value = len(unique_indices) and last_value == value
        if not is_same_as_last_value and value not in seen_values:
            unique_indices.append(index)
            seen_values.add(value)
            last_value = value
    return np.array(unique_indices)
