import random
import sys
import typing

import numba as nb
import numpy as np
import pandas as pd
from tqdm import tqdm

from ..perfect_tracking import (
    GarbageCollectingPhyloTracker,
    PerfectBacktrackHandle,
)


def _setup_population(
    island_niche_size: int,
    num_islands: int,
    num_niches: int,
) -> typing.Tuple[np.array, GarbageCollectingPhyloTracker]:

    pop_size = island_niche_size * num_islands * num_niches

    pop_arr = np.zeros(pop_size, dtype=np.single)
    pop_tracker = GarbageCollectingPhyloTracker(pop_arr)

    return pop_arr, pop_tracker


# @nb.jit(nopython=True, fastmath=True)
def _do_selection(
    island_niche_size: int,
    tournament_size: int,
    pop_arr: np.array,
) -> np.array:

    num_island_niches = len(pop_arr) // island_niche_size

    tournament_boosters = (
        np.broadcast_to(
            np.repeat(
                np.arange(num_island_niches),
                island_niche_size,
            ),
            shape=(tournament_size, pop_arr.size),
        ).T
        * island_niche_size
    )
    tournament_rosters = (
        np.random.randint(
            0,
            island_niche_size,
            (pop_arr.size, tournament_size),
        )
        + tournament_boosters
    )

    tournament_fitnesses = np.take(pop_arr, tournament_rosters)
    winning_tournament_positions = tournament_fitnesses.argmax(axis=1)

    # https://stackoverflow.com/a/61234228
    winning_tournament_idxs = np.take_along_axis(
        tournament_rosters,
        winning_tournament_positions[:, None],
        axis=1,
    )

    if "pytest" in sys.modules:
        assert len(winning_tournament_idxs.flatten()) == pop_arr.size
        assert np.all(
            np.arange(pop_arr.size) // island_niche_size
            == winning_tournament_idxs.flatten() // island_niche_size
        )

    return winning_tournament_idxs.flatten()


def _apply_mutation(
    pop_arr: np.array,
) -> None:
    pop_arr += np.random.standard_normal(size=len(pop_arr))


@nb.jit(nopython=True)
def _get_island_id(
    population_idx: int,
    island_size: int,
) -> int:
    return population_idx // island_size


@nb.jit(nopython=True)
def _get_niche_id(
    population_idx: int, island_niche_size: int, num_niches: int
) -> int:
    return (population_idx // island_niche_size) % num_niches


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

        pop_arr[np.concatenate((swapfrom_idxs, swapto_idxs))] = pop_arr[
            np.concatenate((swapto_idxs, swapfrom_idxs))
        ]


def _apply_island_swaps(
    pop_arr: np.array,
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

        pop_arr[np.concatenate((swapfrom_idxs, swapto_idxs))] = pop_arr[
            np.concatenate((swapto_idxs, swapfrom_idxs))
        ]


def evolve_fitness_trait_population(
    population_size: int = 1024,
    num_islands: int = 4,
    num_niches: int = 4,
    num_generations: int = 100,
    tournament_size: int = 4,
    p_island_migration: float = 1e-3,
    p_niche_invasion: float = 1e-4,
) -> pd.DataFrame:

    island_size = population_size // num_islands
    island_niche_size = population_size // (num_islands * num_niches)
    assert island_niche_size * num_islands * num_niches == population_size
    assert tournament_size <= island_niche_size

    pop_arr, pop_tracker = _setup_population(
        island_niche_size=island_niche_size,
        num_islands=num_islands,
        num_niches=num_niches,
    )

    for generation in tqdm(range(num_generations)):
        _apply_island_swaps(
            pop_arr,
            num_niches=num_niches,
            island_size=island_size,
            island_niche_size=island_niche_size,
            p_island_swap=p_island_migration,
        )
        _apply_niche_swaps(
            pop_arr,
            num_islands=num_islands,
            num_niches=num_niches,
            island_size=island_size,
            island_niche_size=island_niche_size,
            p_niche_swap=p_niche_invasion,
        )
        _apply_mutation(pop_arr)
        idx_selections = _do_selection(
            island_niche_size=island_niche_size,
            tournament_size=tournament_size,
            pop_arr=pop_arr,
        )

        pop_arr = pop_arr[idx_selections]
        pop_tracker.ElapseGeneration(
            idx_selections,
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
