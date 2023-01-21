import sys

import numpy as np

from ...._auxiliary_lib import count_unique, indices_of_unique, is_in_unit_test
from ...perfect_tracking import GarbageCollectingPhyloTracker


def _apply_island_migrations(
    pop_arr: np.array,
    pop_tracker: GarbageCollectingPhyloTracker,
    num_niches: int,
    island_size: int,
    island_niche_size: int,
    p_island_migration: float,
) -> None:

    num_island_migrations = np.random.binomial(
        n=len(pop_arr),
        p=p_island_migration,
    )
    # end early for no-op
    if island_size == len(pop_arr) or not num_island_migrations:
        return

    copyto_idxs = np.empty(num_island_migrations, dtype=np.int32)
    copyfrom_idxs = np.empty(num_island_migrations, dtype=np.int32)
    num_finalized = 0  # loop until all copyto_idxs are distinct
    while num_finalized < num_island_migrations:
        copyfrom_idxs[num_finalized:] = np.random.randint(
            len(pop_arr), size=num_island_migrations - num_finalized
        )
        copyto_signs = (
            np.random.randint(2, size=num_island_migrations - num_finalized)
            * 2
            - 1
        )
        copyto_idxs[num_finalized:] = (
            copyfrom_idxs[num_finalized:] + copyto_signs * island_size
        )
        # wrap overflow
        copyto_idxs[copyto_idxs >= len(pop_arr)] -= len(pop_arr)

        # move unique to front
        indices_of_unique_ = indices_of_unique(copyto_idxs)
        num_finalized = len(indices_of_unique_)
        copyfrom_idxs[:num_finalized] = copyfrom_idxs[indices_of_unique_]
        copyto_idxs[:num_finalized] = copyto_idxs[indices_of_unique_]

    if is_in_unit_test():
        assert len(copyto_idxs) == len(copyfrom_idxs)
        assert all(
            copyto_idxs // island_niche_size % num_niches
            == copyfrom_idxs // island_niche_size % num_niches
        ), (copyto_idxs, copyfrom_idxs, indices_of_unique_)
        assert np.all(
            copyto_idxs // island_size != copyfrom_idxs // island_size
        )
        assert count_unique(copyto_idxs) == len(copyto_idxs)

    pop_arr[copyto_idxs] = pop_arr[copyfrom_idxs].copy()
    pop_tracker.ApplyLocPasteovers(copyfrom_idxs, copyto_idxs)
