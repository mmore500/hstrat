import numpy as np

from ...._auxiliary_lib import count_unique, indices_of_unique, is_in_unit_test
from ...perfect_tracking import GarbageCollectingPhyloTracker


def _apply_island_migrations(
    pop_arr: np.ndarray,
    pop_tracker: GarbageCollectingPhyloTracker,
    num_niches: int,
    island_size: int,
    island_niche_size: int,
    p_island_migration: float,
) -> None:
    """Copy organisms to neighboring islands, altering `pop_arr` inplace.

    See `evolve_fitness_trait_population` for parameter specifications.
    """

    num_island_migrations = np.random.binomial(
        n=len(pop_arr),
        p=p_island_migration,
    )
    # end early for no-op
    if island_size == len(pop_arr) or not num_island_migrations:
        return

    copyto_locs = np.empty(num_island_migrations, dtype=np.int32)
    copyfrom_locs = np.empty(num_island_migrations, dtype=np.int32)
    num_finalized = 0  # loop until all copyto_locs are distinct
    while num_finalized < num_island_migrations:
        copyfrom_locs[num_finalized:] = np.random.randint(
            len(pop_arr), size=num_island_migrations - num_finalized
        )
        copyto_signs = (
            np.random.randint(2, size=num_island_migrations - num_finalized)
            * 2
            - 1
        )
        copyto_locs[num_finalized:] = (
            copyfrom_locs[num_finalized:] + copyto_signs * island_size
        )
        # wrap overflow
        copyto_locs[copyto_locs >= len(pop_arr)] -= len(pop_arr)

        # move unique to front
        indices_of_unique_ = indices_of_unique(copyto_locs)
        num_finalized = len(indices_of_unique_)
        copyfrom_locs[:num_finalized] = copyfrom_locs[indices_of_unique_]
        copyto_locs[:num_finalized] = copyto_locs[indices_of_unique_]

    if is_in_unit_test():
        assert len(copyto_locs) == len(copyfrom_locs)
        assert all(
            copyto_locs // island_niche_size % num_niches
            == copyfrom_locs // island_niche_size % num_niches
        )
        assert np.all(
            copyto_locs // island_size != copyfrom_locs // island_size
        )
        assert count_unique(copyto_locs) == len(copyto_locs)

    pop_arr[copyto_locs] = pop_arr[copyfrom_locs].copy()
    pop_tracker.ApplyLocPasteovers(copyfrom_locs, copyto_locs)
