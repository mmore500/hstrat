import numpy as np


# adapted from https://stackoverflow.com/a/30489294/17332200
def fill_zeros_with_last(arr: np.ndarray) -> np.ndarray:
    """Replace zeros in array with the nearest preceding non-zero value."""
    prev = np.arange(len(arr))
    prev[arr == 0] = 0
    prev = np.maximum.accumulate(prev)
    return arr[prev]
