import random
import typing

import numpy as np
import pandas as pd
from tqdm import tqdm

from ..perfect_tracking import (
    PerfectBacktrackHandle,
    compile_perfect_backtrack_phylogeny,
)

q = 20


def _setup_population(
    island_niche_size: int,
    num_islands: int,
    num_niches: int,
) -> typing.Tuple[pd.DataFrame, typing.List[PerfectBacktrackHandle]]:
    pop_records = [
        {
            "island": island,
            "genome value": 0.0,
            "niche": niche,
        }
        for island in range(num_islands)
        for niche in range(num_niches)
        for __ in range(island_niche_size)
    ]
    pop_df = pd.DataFrame.from_dict(pop_records)

    common_ancestor = PerfectBacktrackHandle(
        data={
            "island": 0,
            "genome value": 0.0,
            "niche": 0,
        }
    )
    pop_handles = [
        common_ancestor.CreateDescendant(
            data=record,
        )
        for record in pop_records
    ]
    return pop_df, pop_handles


def _do_selection(
    island_niche_size: int,
    tournament_size: int,
    pop_df: pd.DataFrame,
    p_random_selection: float,
) -> typing.List[int]:
    res = []
    # couldn't get better performance by sending everything to numpy array
    # and doing more efficient groupby
    # see https://gist.github.com/mmore500/35bd39e1e26b53cfde6e9da482595932
    # and https://stackoverflow.com/a/43094244
    for (island, niche), group_df in pop_df.groupby(
        ["island", "niche"],
        sort=False,
    ):
        # minimizing operations on group_df gives >50% speedup
        genome_lookup = group_df["genome value"].to_numpy()
        tournament_rosters = np.random.randint(
            len(genome_lookup),
            size=(island_niche_size, tournament_size),
        )
        tournament_fitnesses = genome_lookup[tournament_rosters]
        winning_tournament_positions = tournament_fitnesses.argmax(1)
        winning_genome_lookup_positions = tournament_rosters[
            np.arange(len(tournament_rosters)),
            winning_tournament_positions,
        ]
        winning_idxs = group_df.index.to_numpy()[
            winning_genome_lookup_positions
        ]
        assert len(winning_idxs) == island_niche_size
        res.extend(winning_idxs)

    return res


def _apply_mutation(
    pop_df: pd.DataFrame,
    num_islands: int,
    num_niches: int,
    p_island_migration: float,
    p_niche_invasion: float,
) -> None:
    pop_df["genome value"] += np.random.standard_normal(size=pop_df.shape[0])

    num_niche_invasions = np.random.binomial(
        n=len(pop_df),
        p=p_niche_invasion,
    )
    if num_niches > 1 and num_niche_invasions:
        target_rows = pop_df.sample(n=num_niche_invasions)
        target_rows["niche"] += np.random.randint(
            num_niches - 1,
            size=target_rows.shape[0],
        )
        target_rows["niche"] %= num_niches

    num_island_migrations = np.random.binomial(
        n=len(pop_df),
        p=p_island_migration,
    )
    if num_islands > 1 and num_island_migrations:
        target_rows = pop_df.sample(n=num_island_migrations)
        target_rows["island"] += (
            np.random.randint(2, size=target_rows.shape[0]) * 2 + -1
        )
        target_rows["island"] %= num_islands


def _do_pophandles_turnover(
    cache: np.array,
    idx_selections: typing.List[int],
    pop_df: pd.DataFrame,
    pop_handles: typing.List[PerfectBacktrackHandle],
) -> typing.List[PerfectBacktrackHandle]:
    genome_value_loc = pop_df.columns.get_loc("genome value")
    island_loc = pop_df.columns.get_loc("island")
    niche_loc = pop_df.columns.get_loc("niche")

    arr = np.array(idx_selections)

    cache = cache[idx_selections, :]

    cache = np.roll(cache, 1, axis=1)

    cache[:, 0] = idx_selections

    if not any(cache[:, q - 1]):
        return [pop_handles[idx] for idx in idx_selections], cache
    else:
        lookup = {
            idx: pop_handles[idx].CreateDescendant(
                # create data dict manually for 20% speedup
                # data=pop_df.iloc[idx].to_dict(),
                # data={
                #     "genome value": pop_df.iat[idx, genome_value_loc],
                #     "island": pop_df.iat[idx, island_loc],
                #     "niche": pop_df.iat[idx, niche_loc],
                # },
            )
            for idx in np.unique(cache[:, -1])
        }
        return [lookup[cache[:, -1][idx]] for idx in idx_selections], cache


def _do_popdf_turnover(
    idx_selections: typing.List[int], pop_df: pd.DataFrame
) -> pd.DataFrame:
    return pop_df.iloc[idx_selections]


def evolve_fitness_trait_population(
    population_size: int = 1024,
    num_islands: int = 4,
    num_niches: int = 4,
    num_generations: int = 100,
    tournament_size: int = 4,
    p_island_migration: float = 1e-3,
    p_niche_invasion: float = 1e-4,
    p_random_selection: float = 0.5,
) -> pd.DataFrame:

    island_niche_size = population_size // (num_islands * num_niches)
    assert island_niche_size * num_islands * num_niches == population_size
    assert tournament_size <= island_niche_size

    pop_df, pop_handles = _setup_population(
        island_niche_size=island_niche_size,
        num_islands=num_islands,
        num_niches=num_niches,
    )

    cache = np.zeros(dtype=int, shape=(len(pop_df), q))

    for generation in tqdm(range(num_generations)):
        _apply_mutation(
            pop_df=pop_df,
            num_islands=num_islands,
            num_niches=num_niches,
            p_island_migration=p_island_migration,
            p_niche_invasion=p_niche_invasion,
        )
        idx_selections = _do_selection(
            island_niche_size=island_niche_size,
            tournament_size=tournament_size,
            pop_df=pop_df,
            p_random_selection=p_random_selection,
        )
        pop_handles, cache = _do_pophandles_turnover(
            cache,
            idx_selections,
            pop_df,
            pop_handles,
        )
        pop_df = _do_popdf_turnover(
            idx_selections,
            pop_df,
        )

        # reset index
        pop_df.reset_index(drop=True, inplace=True)

        # could sort to reduce fragmentation, but doesn't help
        # pop_df.sort_values(
        #     by=["island", "niche"],
        #     ignore_index=True,  # resets index
        #     inplace=True,
        # )

    for col in reversed(cache.T):
        pop_handles = [pop_handles[idx].CreateDescendant() for idx in col]

    return compile_perfect_backtrack_phylogeny(pop_handles)
