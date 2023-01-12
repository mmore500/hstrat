import collections
import itertools as it

import alifedata_phyloinformatics_convert as apc
import dendropy as dp
import numpy as np
import pandas as pd

from hstrat import hstrat


def _compare_compiled_phylogenies(
    decantless_phylogeny_df: pd.DataFrame,
    decanting_phylogeny_df: pd.DataFrame,
) -> None:
    # compile tree tracked without decanting
    decantless_tree = apc.alife_dataframe_to_dendropy_tree(
        decantless_phylogeny_df,
    )

    # compile tree tracked with decanting
    assert len(decanting_phylogeny_df) == len(
        decanting_phylogeny_df["id"].unique()
    )
    decanting_tree = apc.alife_dataframe_to_dendropy_tree(
        decanting_phylogeny_df,
    )
    assert sum(1 for __ in decanting_tree.leaf_node_iter()) == sum(
        1 for __ in decantless_tree.leaf_node_iter()
    )
    assert (
        len(set(node.level() for node in decanting_tree.leaf_node_iter())) == 1
    )

    # setup taxa in both trees
    for tree in decanting_tree, decantless_tree:
        for i, n in enumerate(tree):
            n.taxon = tree.taxon_namespace.new_taxon(f"{i}")

    # check phylogenetic trees with and without decanting are identical
    assert collections.Counter(
        node.level() for node in decantless_tree
    ) == collections.Counter(node.level() for node in decanting_tree)
    assert collections.Counter(
        decantless_tree.mrca(taxa=[n1.taxon, n2.taxon]).level()
        for n1, n2 in it.combinations(decantless_tree.leaf_node_iter(), 2)
    ) == collections.Counter(
        decanting_tree.mrca(taxa=[n1.taxon, n2.taxon]).level()
        for n1, n2 in it.combinations(decanting_tree.leaf_node_iter(), 2)
    )


def test_DecantingPhyloTracker():

    # setup population and perfect trackers
    population_size = 20
    common_ancestor = hstrat.PerfectBacktrackHandle()
    handle_population = [
        common_ancestor.CreateDescendant() for __ in range(population_size)
    ]
    tracker = hstrat.DecantingPhyloTracker(population_size=population_size)

    # evolve fixed-size population with random selection
    for generation in range(50):
        parent_idxs = np.random.randint(population_size, size=population_size)
        tracker.ElapseGeneration(parent_idxs)
        handle_population = [
            handle_population[idx].CreateDescendant() for idx in parent_idxs
        ]

    _compare_compiled_phylogenies(
        hstrat.compile_perfect_backtrack_phylogeny(handle_population),
        tracker.CompilePhylogeny(),
    )

    # run more generations
    for generation in range(15):
        parent_idxs = np.random.randint(population_size, size=population_size)
        tracker.ElapseGeneration(parent_idxs)
        handle_population = [
            handle_population[idx].CreateDescendant() for idx in parent_idxs
        ]

    _compare_compiled_phylogenies(
        hstrat.compile_perfect_backtrack_phylogeny(handle_population),
        tracker.CompilePhylogeny(),
    )

    # run more generations, fewer than buffer size
    for generation in range(5):
        parent_idxs = np.random.randint(population_size, size=population_size)
        tracker.ElapseGeneration(parent_idxs)
        handle_population = [
            handle_population[idx].CreateDescendant() for idx in parent_idxs
        ]

    _compare_compiled_phylogenies(
        hstrat.compile_perfect_backtrack_phylogeny(handle_population),
        tracker.CompilePhylogeny(),
    )
