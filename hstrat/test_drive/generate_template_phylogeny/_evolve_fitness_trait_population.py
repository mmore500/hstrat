import typing

import numpy as np
import pandas as pd
from tqdm import tqdm

from ..perfect_tracking import (
    PerfectBacktrackHandle,
    compile_perfect_backtrack_phylogeny,
)


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
        for __ in range(island_niche_size)
        for island in range(num_islands)
        for niche in range(num_niches)
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
) -> typing.List[int]:
    return [
        group_df.sample(n=tournament_size)["genome value"].idxmax()
        for (island, niche), group_df in pop_df.groupby(["island", "niche"])
        for __ in range(island_niche_size)
    ]


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
    if num_niche_invasions:
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
    if num_island_migrations:
        target_rows = pop_df.sample(n=num_island_migrations)
        target_rows["island"] += (
            np.random.randint(2, size=target_rows.shape[0]) * 2 + -1
        )
        target_rows["island"] %= num_islands


def _do_pophandles_turnover(
    idx_selections: typing.List[int],
    pop_df: pd.DataFrame,
    pop_handles: typing.List[PerfectBacktrackHandle],
) -> typing.List[PerfectBacktrackHandle]:
    return [
        pop_handles[idx].CreateDescendant(
            data=pop_df.iloc[idx].to_dict(),
        )
        for idx in idx_selections
    ]


def _do_popdf_turnover(
    idx_selections: typing.List[int], pop_df: pd.DataFrame
) -> pd.DataFrame:
    return pop_df.iloc[idx_selections].reset_index(drop=True)


def evolve_fitness_trait_population(
    population_size: int = 1024,
    num_islands: int = 4,
    num_niches: int = 4,
    num_generations: int = 100,
    tournament_size: int = 4,
    p_island_migration: float = 1e-3,
    p_niche_invasion: float = 1e-4,
) -> pd.DataFrame:

    island_niche_size = population_size // (num_islands * num_niches)
    assert island_niche_size * num_islands * num_niches == population_size
    assert tournament_size <= island_niche_size

    pop_df, pop_handles = _setup_population(
        island_niche_size=island_niche_size,
        num_islands=num_islands,
        num_niches=num_niches,
    )

    for generation in tqdm(range(num_generations)):
        idx_selections = _do_selection(
            island_niche_size=island_niche_size,
            tournament_size=tournament_size,
            pop_df=pop_df,
        )
        _apply_mutation(
            pop_df=pop_df,
            num_islands=num_islands,
            num_niches=num_niches,
            p_island_migration=p_island_migration,
            p_niche_invasion=p_niche_invasion,
        )
        pop_handles = _do_pophandles_turnover(
            idx_selections,
            pop_df,
            pop_handles,
        )
        pop_df = _do_popdf_turnover(
            idx_selections,
            pop_df,
        )

    return compile_perfect_backtrack_phylogeny(pop_handles)
