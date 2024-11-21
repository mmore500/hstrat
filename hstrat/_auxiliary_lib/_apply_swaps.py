import numpy as np

from ._jit import jit


@jit(nopython=True)
def apply_swaps(
    arr: np.ndarray, swapfrom_idxs: np.ndarray, swapto_idxs: np.ndarray
) -> None:
    """Swap elements in `arr` at `swapfrom_idxs` indices with elements at
    `swapto_idxs` indices.

    The elements at the first index in `swapfrom_idxs` and the first index in
    `swapfrom_idxs` are swapped, then elements at the second indices in the
    the argument arrays, and so on. Swaps are applied to `arr` inplace.
    """
    for a, b in zip(swapfrom_idxs, swapto_idxs):
        arr[a], arr[b] = arr[b], arr[a]
