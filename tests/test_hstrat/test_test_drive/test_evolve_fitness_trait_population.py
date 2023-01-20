import itertools as it
import os

import alifedata_phyloinformatics_convert as apc
import dendropy as dp
import pandas as pd
import pytest
from tqdm import tqdm

from hstrat import hstrat
from hstrat._auxiliary_lib import pairwise, zip_strict

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

    assert all(
        0 <= island <= num_islands for island in alife_df["island"]
    ), alife_df["island"]
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
