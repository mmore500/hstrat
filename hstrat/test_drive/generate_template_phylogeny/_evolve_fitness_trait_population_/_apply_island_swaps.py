import sys

import numpy as np

from ...._auxiliary_lib import apply_swaps
from ...perfect_tracking import GarbageCollectingPhyloTracker


def _apply_island_swaps(
    pop_arr: np.array,
    pop_tracker: GarbageCollectingPhyloTracker,
    num_niches: int,
    island_size: int,
    island_niche_size: int,
    p_island_swap: float,
) -> None:

    num_island_swaps = np.random.binomial(
        n=len(pop_arr),
        p=p_island_swap,
    )
    if island_size < len(pop_arr) and num_island_swaps:

        swapfrom_idxs = np.random.randint(len(pop_arr), size=num_island_swaps)
        swapto_signs = np.random.randint(2, size=num_island_swaps) * 2 - 1
        swapto_idxs = swapfrom_idxs + swapto_signs * island_size
        # wrap overflow
        swapto_idxs[swapto_idxs >= len(pop_arr)] -= len(pop_arr)

        if "pytest" in sys.modules:
            assert len(swapto_idxs) == len(swapfrom_idxs)
            assert all(
                swapto_idxs // island_niche_size % num_niches
                == swapfrom_idxs // island_niche_size % num_niches
            )
            assert np.all(
                swapto_idxs // island_size != swapfrom_idxs // island_size
            )

        apply_swaps(pop_arr, swapfrom_idxs, swapto_idxs)
        pop_tracker.ApplyLocSwaps(swapfrom_idxs, swapto_idxs)
