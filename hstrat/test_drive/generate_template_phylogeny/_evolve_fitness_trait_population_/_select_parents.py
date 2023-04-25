import numpy as np

from ...._auxiliary_lib import is_in_unit_test


def _select_parents(
    island_niche_size: int,
    tournament_size: int,
    pop_arr: np.array,
) -> np.array:
    """Perform tournament selection within island-niches.

    The population array `pop_arr` is not altered.

    Returns
    -------
    numpy.array of int
        Population locations (i.e., indices) specifying the parent for each
        population slot at the next generation.

        Position within array corresponds to post-turnover population members'
        population positions. Values within array correspond to those members'
        parents' population positions within the pre-turnover population.
    """
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
    winning_tournament_locs = np.take_along_axis(
        tournament_rosters,
        winning_tournament_positions[:, None],
        axis=1,
    )

    if is_in_unit_test():
        assert len(winning_tournament_locs.flatten()) == pop_arr.size
        assert np.all(
            np.arange(pop_arr.size) // island_niche_size
            == winning_tournament_locs.flatten() // island_niche_size
        )

    return winning_tournament_locs.flatten()
