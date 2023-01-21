import numpy as np

from ._jit_if_has_numba import jit_if_has_numba


@jit_if_has_numba(nopython=True)
def apply_swaps(
    arr: np.array, swapfrom_idxs: np.array, swapto_idxs: np.array
) -> None:
    for a, b in zip(swapfrom_idxs, swapto_idxs):
        arr[a], arr[b] = arr[b], arr[a]
