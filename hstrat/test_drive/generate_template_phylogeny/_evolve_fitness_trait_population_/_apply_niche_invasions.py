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
    """Copy organisms to a new niche, altering `pop_arr` inplace.

    See `evolve_fitness_trait_population` for parameter specifications.
    """

    num_niche_invasions = np.random.binomial(
        n=len(pop_arr),
        p=p_niche_invasion,
    )

    # end early for no-op
    if num_niches == 1 or not num_niche_invasions:
        return

    copyto_locs = np.empty(num_niche_invasions, dtype=np.int32)
    copyfrom_locs = np.empty(num_niche_invasions, dtype=np.int32)
    num_finalized = 0  # loop until all copyto_locs are distinct
    while num_finalized < num_niche_invasions:
        copyfrom_locs[num_finalized:] = np.random.randint(
            len(pop_arr), size=(num_niche_invasions - num_finalized)
        )
        copyfrom_niches = (
            copyfrom_locs[num_finalized:] // island_niche_size
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

        copyto_locs[num_finalized:] = (
            copyfrom_locs[num_finalized:] + swap_steps
        )
        # move unique to front
        indices_of_unique_ = indices_of_unique(copyto_locs)
        num_finalized = len(indices_of_unique_)
        copyfrom_locs[:num_finalized] = copyfrom_locs[indices_of_unique_]
        copyto_locs[:num_finalized] = copyto_locs[indices_of_unique_]

    if is_in_unit_test():
        assert len(copyto_locs) == len(copyfrom_locs)
        assert np.all(
            copyto_locs // island_size == copyfrom_locs // island_size
        )
        assert all(
            copyto_locs // island_niche_size % num_niches
            != copyfrom_locs // island_niche_size % num_niches
        )
        assert count_unique(copyto_locs) == len(copyto_locs)

    pop_arr[copyto_locs] = pop_arr[copyfrom_locs].copy()
    pop_tracker.ApplyLocPasteovers(copyfrom_locs, copyto_locs)
