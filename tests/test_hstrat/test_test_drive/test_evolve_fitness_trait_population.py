import os

import alifedata_phyloinformatics_convert as apc
import numpy as np
import pytest
from tqdm import tqdm

from hstrat import hstrat
from hstrat._auxiliary_lib import omit_last

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize(
    "num_islands",
    [
        1,
        4,
    ],
)
@pytest.mark.parametrize(
    "num_niches",
    [
        1,
        4,
    ],
)
@pytest.mark.parametrize(
    "num_generations",
    [
        10,
        200,
    ],
)
@pytest.mark.parametrize(
    "population_size",
    [
        128,
        256,
    ],
)
def test_evolve_fitness_trait_population(
    num_islands,
    num_niches,
    num_generations,
    population_size,
):
    alife_df = hstrat.evolve_fitness_trait_population(
        num_islands=num_islands,
        num_niches=num_niches,
        num_generations=num_generations,
        population_size=population_size,
        tournament_size=2,
        progress_wrap=tqdm,
    )

    assert "trait" in alife_df
    assert "loc" in alife_df
    assert "island" in alife_df
    assert "niche" in alife_df

    assert all(0 <= island <= num_islands for island in alife_df["island"])
    assert all(0 <= niche <= num_niches for niche in alife_df["niche"])
    assert num_islands * num_niches == len(
        set(
            (island, niche)
            for __, (island, niche) in alife_df[["island", "niche"]].iterrows()
        )
    )

    tree = apc.alife_dataframe_to_dendropy_tree(alife_df)

    assert len(tree) == population_size
    assert len(set(leaf_node.level() for leaf_node in tree.leaf_node_iter()))
    assert all(
        leaf_node.level() == num_generations + 1
        for leaf_node in tree.leaf_node_iter()
    )


@pytest.mark.parametrize(
    "num_islands",
    [
        1,
        4,
    ],
)
@pytest.mark.parametrize(
    "num_niches",
    [
        1,
        4,
    ],
)
@pytest.mark.parametrize(
    "p_island_migration",
    [
        0.0,
        0.1,
        1.0,
    ],
)
@pytest.mark.parametrize(
    "p_niche_invasion",
    [
        0.0,
        0.1,
        1.0,
    ],
)
@pytest.mark.parametrize(
    "mut_distn",
    [
        np.random.standard_normal,
        np.random.laplace,
        lambda size: np.zeros(shape=size),
    ],
)
def test_evolve_fitness_trait_population_swaps(
    num_islands,
    num_niches,
    p_island_migration,
    p_niche_invasion,
    mut_distn,
):
    alife_df = hstrat.evolve_fitness_trait_population(
        num_islands=num_islands,
        num_niches=num_niches,
        num_generations=200,
        population_size=128,
        p_island_migration=p_island_migration,
        p_niche_invasion=p_niche_invasion,
        mut_distn=mut_distn,
        progress_wrap=tqdm,
    )

    assert "trait" in alife_df
    assert "loc" in alife_df
    assert "island" in alife_df
    assert "niche" in alife_df

    tree = apc.alife_dataframe_to_dendropy_tree(
        alife_df,
        setattrs=("island", "niche"),
    )

    assert any(
        len(
            set(
                ancestor.island
                for ancestor in omit_last(leaf.ancestor_iter(inclusive=True))
            )
        )
        > 1
        for leaf in tree.leaf_node_iter()
    ) == (p_island_migration and num_islands > 1)
    assert any(
        len(
            set(
                ancestor.niche
                for ancestor in omit_last(leaf.ancestor_iter(inclusive=True))
            )
        )
        > 1
        for leaf in tree.leaf_node_iter()
    ) == (p_niche_invasion and num_niches > 1)


def test_evolve_fitness_trait_population_selection():
    drift_alife_df = hstrat.evolve_fitness_trait_population(
        num_generations=200,
        population_size=128,
        tournament_size=1,
        progress_wrap=tqdm,
    )
    drift_tree = apc.alife_dataframe_to_dendropy_tree(
        drift_alife_df,
        setattrs=("trait",),
    )
    drift_tree_mean_fitness = np.mean(
        [node.trait for node in drift_tree.leaf_node_iter()]
    )

    weak_alife_df = hstrat.evolve_fitness_trait_population(
        num_generations=200,
        population_size=128,
        tournament_size=2,
        progress_wrap=tqdm,
    )
    weak_tree = apc.alife_dataframe_to_dendropy_tree(
        weak_alife_df,
        setattrs=("trait",),
    )
    weak_tree_mean_fitness = np.mean(
        [node.trait for node in weak_tree.leaf_node_iter()]
    )

    weak_bigpop_alife_df = hstrat.evolve_fitness_trait_population(
        num_generations=200,
        population_size=1024,
        tournament_size=2,
        progress_wrap=tqdm,
    )
    weak_bigpop_tree = apc.alife_dataframe_to_dendropy_tree(
        weak_bigpop_alife_df,
        setattrs=("trait",),
    )
    weak_bigpop_tree_mean_fitness = np.mean(
        [node.trait for node in weak_bigpop_tree.leaf_node_iter()]
    )

    strong_alife_df = hstrat.evolve_fitness_trait_population(
        num_generations=200,
        population_size=128,
        tournament_size=7,
        progress_wrap=tqdm,
    )
    strong_tree = apc.alife_dataframe_to_dendropy_tree(
        strong_alife_df,
        setattrs=("trait",),
    )
    strong_tree_mean_fitness = np.mean(
        [node.trait for node in strong_tree.leaf_node_iter()]
    )

    assert (
        drift_tree_mean_fitness
        < weak_tree_mean_fitness
        < strong_tree_mean_fitness
    )

    assert weak_tree_mean_fitness < weak_bigpop_tree_mean_fitness

    assert sum(1 for __ in drift_tree) > sum(1 for __ in strong_tree)


@pytest.mark.parametrize(
    "num_generations",
    [
        100,
        200,
    ],
)
@pytest.mark.parametrize(
    "population_size",
    [
        128,
        256,
    ],
)
@pytest.mark.parametrize(
    "share_common_ancestor",
    [
        True,
        False,
    ],
)
def test_evolve_fitness_trait_population_iter_epochs(
    num_generations,
    population_size,
    share_common_ancestor,
):

    epoch_iter = hstrat.evolve_fitness_trait_population(
        iter_epochs=True,
        num_generations=num_generations,
        population_size=population_size,
        share_common_ancestor=share_common_ancestor,
        progress_wrap=tqdm,
    )

    dfs = [next(epoch_iter) for __ in range(3)]

    series_sets = [
        set(
            # id and ancestor_list (ancestor id) depend on position within
            # extant organisms, so aren't conserved
            df.drop(["id", "ancestor_list"], axis=1).apply(
                tuple,
                axis=1,
            )
        )
        for df in dfs
    ]

    assert len(series_sets[0] & series_sets[1]) > num_generations - 1
    assert len(series_sets[0] & series_sets[2]) > num_generations * 2 - 1

    for epoch, df in enumerate(dfs):
        assert all(
            leaf_node.level()
            == (epoch + 1) * num_generations + share_common_ancestor
            for tree in apc.alife_dataframe_to_dendropy_trees(df)
            for leaf_node in tree.leaf_node_iter()
        )
