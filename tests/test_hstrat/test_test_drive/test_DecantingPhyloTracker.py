import collections
import itertools as it

import alifedata_phyloinformatics_convert as apc
import numpy as np
import pandas as pd
import pytest

from hstrat import hstrat


def _compare_compiled_phylogenies(
    decantless_phylogeny_df: pd.DataFrame,
    decanting_phylogeny_df: pd.DataFrame,
    share_common_ancestor: bool,
) -> None:
    # compile tree tracked without decanting
    decantless_trees = apc.alife_dataframe_to_dendropy_trees(
        decantless_phylogeny_df,
    )
    if share_common_ancestor:
        assert len(decantless_trees) == 1

    # compile tree tracked with decanting
    assert len(decanting_phylogeny_df) == len(
        decanting_phylogeny_df["id"].unique()
    )

    decanting_trees = apc.alife_dataframe_to_dendropy_trees(
        decanting_phylogeny_df,
    )
    assert sum(
        1
        for decanting_tree in decanting_trees
        for __ in decanting_tree.leaf_node_iter()
    ) == sum(
        1
        for decantless_tree in decantless_trees
        for __ in decantless_tree.leaf_node_iter()
    )
    assert (
        len(
            set(
                node.level()
                for decanting_tree in decantless_trees
                for node in decanting_tree.leaf_node_iter()
            )
        )
        == 1
    )

    assert len(decanting_trees) == len(decantless_trees)

    # setup taxa in both trees
    for trees in decanting_trees, decantless_trees:
        for i, tree in enumerate(trees):
            for j, n in enumerate(tree):
                n.taxon = tree.taxon_namespace.new_taxon(f"{i} {j}")

    # check phylogenetic trees with and without decanting are identical
    assert collections.Counter(
        node.level()
        for decantless_tree in decantless_trees
        for node in decantless_tree
    ) == collections.Counter(
        node.level()
        for decanting_tree in decanting_trees
        for node in decanting_tree
    )
    assert collections.Counter(
        decantless_tree.mrca(taxa=[n1.taxon, n2.taxon]).level()
        for decantless_tree in decantless_trees
        for n1, n2 in it.combinations(decantless_tree.leaf_node_iter(), 2)
    ) == collections.Counter(
        decanting_tree.mrca(taxa=[n1.taxon, n2.taxon]).level()
        for decanting_tree in decanting_trees
        for n1, n2 in it.combinations(decanting_tree.leaf_node_iter(), 2)
    )


@pytest.mark.parametrize(
    "population_size",
    [
        20,
        100,
    ],
)
@pytest.mark.parametrize(
    "share_common_ancestor",
    [
        True,
        False,
    ],
)
def test_DecantingPhyloTracker(population_size, share_common_ancestor):

    # setup population and perfect trackers
    common_ancestor = hstrat.PerfectBacktrackHandle()
    handle_population = (
        [common_ancestor.CreateDescendant() for __ in range(population_size)]
        if share_common_ancestor
        else [hstrat.PerfectBacktrackHandle() for __ in range(population_size)]
    )
    tracker = hstrat.DecantingPhyloTracker(
        population_size=population_size,
        share_common_ancestor=share_common_ancestor,
    )

    # evolve fixed-size population with random selection
    for epoch_length in 0, 3, 50, 15, 5:
        for generation in range(epoch_length):
            parent_locs = np.random.randint(
                population_size, size=population_size
            )
            tracker.ElapseGeneration(parent_locs)
            handle_population = [
                handle_population[loc].CreateDescendant()
                for loc in parent_locs
            ]

        _compare_compiled_phylogenies(
            hstrat.compile_perfect_backtrack_phylogeny(handle_population),
            tracker.CompilePhylogeny(),
            share_common_ancestor,
        )
