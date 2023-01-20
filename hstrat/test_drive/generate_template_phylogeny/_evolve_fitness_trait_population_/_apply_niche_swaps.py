import sys

import numpy as np

from ...._auxiliary_lib import apply_swaps


def _apply_niche_swaps(
    pop_arr: np.array,
    num_islands: int,
    num_niches: int,
    island_size: int,
    island_niche_size: int,
    p_niche_swap: float,
) -> None:

    num_niche_swaps = np.random.binomial(
        n=len(pop_arr),
        p=p_niche_swap,
    )
    if num_niches > 1 and num_niche_swaps:

        swapfrom_idxs = np.random.randint(len(pop_arr), size=num_niche_swaps)
        swapfrom_niches = (swapfrom_idxs // island_niche_size) % num_niches

        niche_steps = np.random.randint(num_niches - 1, size=num_niche_swaps)
        corrected_niche_steps = (
            niche_steps + (niche_steps >= swapfrom_niches) - swapfrom_niches
        )
        assert np.all(corrected_niche_steps != 0)
        swap_steps = corrected_niche_steps * island_niche_size

        swapto_idxs = swapfrom_idxs + swap_steps

        if "pytest" in sys.modules:
            assert np.all(abs(swap_steps) < island_size)
            assert len(swapto_idxs) == len(swapfrom_idxs)
            assert np.all(
                swapto_idxs // island_size == swapfrom_idxs // island_size
            )
            assert all(
                swapto_idxs // island_niche_size % num_niches
                != swapfrom_idxs // island_niche_size % num_niches
            )

        apply_swaps(pop_arr, swapfrom_idxs, swapto_idxs)
