import numpy as np

from ._jit import jit


@jit(nopython=True)
def indices_of_unique(array: np.ndarray) -> np.ndarray:
    """Return the indices where the first occurance of each unique value in
    `array` occurs.

    Equivalent to `return_index` functionality of `numpy.unique`, but faster.
    See <https://numpy.org/doc/1.24/reference/generated/numpy.unique.html>.
    """
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
