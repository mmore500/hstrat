import sys

import numpy as np


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
