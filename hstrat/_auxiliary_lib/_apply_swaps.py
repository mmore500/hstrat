import numba as nb
import numpy as np


@nb.jit(nopython=True)
def apply_swaps(
    arr: np.array, swapfrom_idxs: np.array, swapto_idxs: np.array
) -> None:
    for a, b in zip(swapfrom_idxs, swapto_idxs):
        arr[a], arr[b] = arr[b], arr[a]
