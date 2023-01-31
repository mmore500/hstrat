import itertools as it
import os

import alifedata_phyloinformatics_convert as apc
import pandas as pd
import pytest

from hstrat import hstrat
from hstrat._auxiliary_lib import seed_random

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize(
    "stratum_ordered_store",
    hstrat.provided_stratum_ordered_stores,
)
@pytest.mark.parametrize(
    "stratum_retention_algorithm",
    hstrat.provided_stratum_retention_algorithms,
)
def test_genome_instrumentation_deterministic(
    stratum_ordered_store, stratum_retention_algorithm
):
    try:
        policy = stratum_retention_algorithm.Policy()
    except TypeError:
        policy = stratum_retention_algorithm.Policy(1)

    derived_columns = []
    for _rep in range(3):
        seed_random(1)
        col = hstrat.HereditaryStratigraphicColumn(
            stratum_retention_policy=policy,
            stratum_ordered_store=stratum_ordered_store,
        )
        for __ in range(50):
            col.DepositStratum()

        col.DepositStrata(10)

        col = col.CloneDescendant()

        col = col.CloneNthDescendant(10)

        derived_columns.append(col)

    for a, b in it.combinations(derived_columns, 2):
        assert a == b

    # control test
    derived_columns = []
    for rep in range(3):
        seed_random(rep)
        col = hstrat.HereditaryStratigraphicColumn(
            stratum_retention_policy=policy,
            stratum_ordered_store=stratum_ordered_store,
        )
        for __ in range(50):
            col.DepositStratum()

        col.DepositStrata(10)

        col = col.CloneDescendant()

        col = col.CloneNthDescendant(10)

        derived_columns.append(col)

    for a, b in it.combinations(derived_columns, 2):
        assert a != b


def test_template_phylogeny_generation_determinstic():
    derived_phylogenetic_records = []
    for _rep in range(3):
        seed_random(1)

        derived_phylogenetic_records.append(
            hstrat.evolve_fitness_trait_population()
        )

    for a, b in it.combinations(derived_phylogenetic_records, 2):
        assert a.equals(b)

    # control test
    derived_phylogenetic_records = []
    for rep in range(3):
        seed_random(rep)

        derived_phylogenetic_records.append(
            hstrat.evolve_fitness_trait_population()
        )

    for a, b in it.combinations(derived_phylogenetic_records, 2):
        assert not a.equals(b)


@pytest.mark.parametrize(
    "stratum_retention_algorithm",
    hstrat.provided_stratum_retention_algorithms,
)
@pytest.mark.parametrize(
    "tree",
    [
        apc.alife_dataframe_to_dendropy_tree(
            pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
            setup_edge_lengths=True,
        ),
        apc.alife_dataframe_to_dendropy_tree(
            pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
            setup_edge_lengths=True,
        ),
        apc.alife_dataframe_to_dendropy_tree(
            pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
            setup_edge_lengths=True,
        ),
    ],
)
def test_template_phylogeny_descent_deterministic(
    stratum_retention_algorithm,
    tree,
):
    try:
        policy = stratum_retention_algorithm.Policy()
    except TypeError:
        policy = stratum_retention_algorithm.Policy(1)

    derived_column_populations = []
    for _rep in range(3):
        seed_random(1)

        seed_column = hstrat.HereditaryStratigraphicColumn(
            stratum_retention_policy=policy,
        )

        extant_population = hstrat.descend_template_phylogeny(
            ascending_lineage_iterables=(
                tip_node.ancestor_iter(
                    inclusive=True,
                )
                for tip_node in tree.leaf_node_iter()
            ),
            descending_tree_iterable=tree.levelorder_node_iter(),
            get_parent=lambda node: node.parent_node,
            get_stem_length=lambda node: node.edge_length,
            seed_column=seed_column,
        )

        derived_column_populations.append(extant_population)

    for a, b in it.combinations(derived_column_populations, 2):
        assert a == b

    # control test
    derived_column_populations = []
    for rep in range(3):
        seed_random(rep)

        seed_column = hstrat.HereditaryStratigraphicColumn(
            stratum_retention_policy=policy,
        )

        extant_population = hstrat.descend_template_phylogeny(
            ascending_lineage_iterables=(
                tip_node.ancestor_iter(
                    inclusive=True,
                )
                for tip_node in tree.leaf_node_iter()
            ),
            descending_tree_iterable=tree.levelorder_node_iter(),
            get_parent=lambda node: node.parent_node,
            get_stem_length=lambda node: node.edge_length,
            seed_column=seed_column,
        )

        derived_column_populations.append(extant_population)

    for a, b in it.combinations(derived_column_populations, 2):
        assert a != b
