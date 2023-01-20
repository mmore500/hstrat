import typing

import numpy as np
import pandas as pd
from tqdm import tqdm

from ..perfect_tracking import GarbageCollectingPhyloTracker
from ._evolve_fitness_trait_population_ import (
    _apply_island_swaps,
    _apply_mutation,
    _apply_niche_swaps,
    _get_island_id,
    _get_niche_id,
    _select_parents,
)


def evolve_fitness_trait_population(
    population_size: int = 1024,
    num_islands: int = 4,
    num_niches: int = 4,
    num_generations: int = 100,
    tournament_size: int = 4,
    p_island_swap: float = 1e-3,
    p_niche_swap: float = 1e-4,
    progress_wrap: typing.Callable = lambda x: x,
) -> pd.DataFrame:

    island_size = population_size // num_islands
    island_niche_size = population_size // (num_islands * num_niches)
    assert island_niche_size * num_islands * num_niches == population_size
    assert tournament_size <= island_niche_size

    pop_arr = np.zeros(population_size, dtype=np.single)
    pop_tracker = GarbageCollectingPhyloTracker(pop_arr)

    for generation in progress_wrap(range(num_generations)):
        _apply_island_swaps(
            pop_arr,
            pop_tracker,
            num_niches=num_niches,
            island_size=island_size,
            island_niche_size=island_niche_size,
            p_island_swap=p_island_swap,
        )
        _apply_niche_swaps(
            pop_arr,
            pop_tracker,
            num_islands=num_islands,
            num_niches=num_niches,
            island_size=island_size,
            island_niche_size=island_niche_size,
            p_niche_swap=p_niche_swap,
        )
        _apply_mutation(pop_arr)
        parent_idxs = _select_parents(
            island_niche_size=island_niche_size,
            tournament_size=tournament_size,
            pop_arr=pop_arr,
        )

        pop_arr = pop_arr[parent_idxs]
        pop_tracker.ElapseGeneration(
            parent_idxs,
            pop_arr,
        )

    return pop_tracker.CompilePhylogeny(
        loc_transforms={
            "island": lambda loc: _get_island_id(loc, island_size),
            "niche": lambda loc: _get_niche_id(
                loc, island_niche_size, num_niches
            ),
        },
        progress_wrap=tqdm,
    )
