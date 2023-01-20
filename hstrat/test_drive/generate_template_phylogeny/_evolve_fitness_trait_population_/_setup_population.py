import typing

import numpy as np

from ...perfect_tracking import GarbageCollectingPhyloTracker


def _setup_population(
    island_niche_size: int,
    num_islands: int,
    num_niches: int,
) -> typing.Tuple[np.array, GarbageCollectingPhyloTracker]:

    pop_size = island_niche_size * num_islands * num_niches

    pop_arr = np.zeros(pop_size, dtype=np.single)
    pop_tracker = GarbageCollectingPhyloTracker(pop_arr)

    return pop_arr, pop_tracker
