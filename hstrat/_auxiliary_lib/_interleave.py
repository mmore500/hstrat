import numpy as np


# adapted from https://stackoverflow.com/a/5347492
def interleave(a: np.array, b: np.array) -> np.array:
    res = np.empty(a.size + b.size, dtype=a.dtype)
    res[0::2] = a
    res[1::2] = b
    return res
