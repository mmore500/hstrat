import sys

import numpy as np

from ...._auxiliary_lib import count_unique, indices_of_unique, is_in_unit_test
from ...perfect_tracking import GarbageCollectingPhyloTracker


def _apply_niche_invasions(
    pop_arr: np.array,
    pop_tracker: GarbageCollectingPhyloTracker,
    num_islands: int,
    num_niches: int,
    island_size: int,
    island_niche_size: int,
    p_niche_invasion: float,
) -> None:

    num_niche_invasions = np.random.binomial(
        n=len(pop_arr),
        p=p_niche_invasion,
    )

    # end early for no-op
    if num_niches == 1 or not num_niche_invasions:
        return

    copyto_idxs = np.empty(num_niche_invasions, dtype=np.int32)
    copyfrom_idxs = np.empty(num_niche_invasions, dtype=np.int32)
    num_finalized = 0  # loop until all copyto_idxs are distinct
    while num_finalized < num_niche_invasions:
        copyfrom_idxs[num_finalized:] = np.random.randint(
            len(pop_arr), size=(num_niche_invasions - num_finalized)
        )
        copyfrom_niches = (
            copyfrom_idxs[num_finalized:] // island_niche_size
        ) % num_niches

        niche_steps = np.random.randint(
            num_niches - 1, size=(num_niche_invasions - num_finalized)
        )
        corrected_niche_steps = (
            niche_steps + (niche_steps >= copyfrom_niches) - copyfrom_niches
        )
        assert np.all(corrected_niche_steps != 0)
        swap_steps = corrected_niche_steps * island_niche_size
        if is_in_unit_test():
            assert np.all(abs(swap_steps) < island_size)

        copyto_idxs[num_finalized:] = (
            copyfrom_idxs[num_finalized:] + swap_steps
        )
        # move unique to front
        indices_of_unique_ = indices_of_unique(copyto_idxs)
        num_finalized = len(indices_of_unique_)
        copyfrom_idxs[:num_finalized] = copyfrom_idxs[indices_of_unique_]
        copyto_idxs[:num_finalized] = copyto_idxs[indices_of_unique_]

    if is_in_unit_test():
        assert len(copyto_idxs) == len(copyfrom_idxs)
        assert np.all(
            copyto_idxs // island_size == copyfrom_idxs // island_size
        ), (copyto_idxs, copyfrom_idxs)
        assert all(
            copyto_idxs // island_niche_size % num_niches
            != copyfrom_idxs // island_niche_size % num_niches
        ), (copyto_idxs, copyfrom_idxs)
        assert count_unique(copyto_idxs) == len(copyto_idxs)

    pop_arr[copyto_idxs] = pop_arr[copyfrom_idxs].copy()
    pop_tracker.ApplyLocPasteovers(copyfrom_idxs, copyto_idxs)
