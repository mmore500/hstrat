import collections
from copy import copy
import itertools as it

import alifedata_phyloinformatics_convert as apc
import numpy as np
import pandas as pd
import pytest

from hstrat import hstrat
from hstrat._auxiliary_lib import omit_last


def _compare_compiled_phylogenies(
    control_phylogeny_df: pd.DataFrame,
    test_phylogeny_df: pd.DataFrame,
    share_common_ancestor: bool,
) -> None:
    # compile tree tracked with handle tracker
    control_trees = apc.alife_dataframe_to_dendropy_trees(
        control_phylogeny_df,
    )
    if share_common_ancestor:
        assert len(control_trees) == 1

    # compile tree tracked with gc tracker
    assert len(test_phylogeny_df) == len(test_phylogeny_df["id"].unique())

    test_trees = apc.alife_dataframe_to_dendropy_trees(
        test_phylogeny_df,
    )
    assert sum(
        1 for test_tree in test_trees for __ in test_tree.leaf_node_iter()
    ) == sum(
        1
        for control_tree in control_trees
        for __ in control_tree.leaf_node_iter()
    )
    assert (
        len(
            set(
                node.level()
                for test_tree in control_trees
                for node in test_tree.leaf_node_iter()
            )
        )
        == 1
    )
    assert all(
        node.level() == node.origin_time
        for test_tree in test_trees
        for node in test_tree
    )

    assert len(test_trees) == len(control_trees)

    # setup taxa in both trees
    for trees in test_trees, control_trees:
        for i, tree in enumerate(trees):
            for j, n in enumerate(tree):
                n.taxon = tree.taxon_namespace.new_taxon(f"{i} {j}")

    # check phylogenetic trees with and without test are identical
    assert collections.Counter(
        node.level() for control_tree in control_trees for node in control_tree
    ) == collections.Counter(
        node.level() for test_tree in test_trees for node in test_tree
    )
    assert collections.Counter(
        control_tree.mrca(taxa=[n1.taxon, n2.taxon]).level()
        for control_tree in control_trees
        for n1, n2 in it.combinations(control_tree.leaf_node_iter(), 2)
    ) == collections.Counter(
        test_tree.mrca(taxa=[n1.taxon, n2.taxon]).level()
        for test_tree in test_trees
        for n1, n2 in it.combinations(test_tree.leaf_node_iter(), 2)
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
@pytest.mark.parametrize(
    "working_buffer_size_mx",
    [
        1,
        10,
    ],
)
def test_GarbageCollectingPhyloTracker(
    population_size, share_common_ancestor, working_buffer_size_mx
):

    # setup population and perfect trackers
    common_ancestor = hstrat.PerfectBacktrackHandle()
    handle_population = (
        [common_ancestor.CreateDescendant() for __ in range(population_size)]
        if share_common_ancestor
        else [hstrat.PerfectBacktrackHandle() for __ in range(population_size)]
    )
    tracker = hstrat.GarbageCollectingPhyloTracker(
        initial_population=population_size,
        share_common_ancestor=share_common_ancestor,
        working_buffer_size=population_size * working_buffer_size_mx + 1,
    )

    # evolve fixed-size population with random selection
    for epoch_length in 0, 3, 50, 15, 5:
        for _generation in range(epoch_length):
            _ = _generation
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


def test_GarbateCollectingPhyloTracker_ApplyLocSwaps():

    # setup population and perfect trackers
    population_size = 4
    common_ancestor = hstrat.PerfectBacktrackHandle(data=0)
    handle_population = [
        common_ancestor.CreateDescendant(data=loc)
        for loc in range(population_size)
    ]
    tracker = hstrat.GarbageCollectingPhyloTracker(
        initial_population=population_size,
        working_buffer_size=21,
    )

    # evolve fixed-size population with random selection
    for _generation in range(50):
        _ = _generation
        parent_locs = np.random.randint(population_size, size=population_size)
        tracker.ElapseGeneration(parent_locs)
        handle_population = [
            handle_population[loc].CreateDescendant() for loc in parent_locs
        ]

        swapfrom_locs = np.random.randint(
            population_size, size=population_size
        )
        swapto_locs = np.random.randint(population_size, size=population_size)

        tracker.ApplyLocSwaps(swapfrom_locs, swapto_locs)
        for from_loc, to_loc in zip(swapfrom_locs, swapto_locs):
            handle_population[from_loc], handle_population[to_loc] = (
                handle_population[to_loc],
                handle_population[from_loc],
            )

        for loc, handle in enumerate(handle_population):
            handle.data = loc

    handle_alife_df = hstrat.compile_perfect_backtrack_phylogeny(
        handle_population
    )
    handle_tree = apc.alife_dataframe_to_dendropy_tree(
        handle_alife_df,
        setattrs={"data": "loc"},
    )
    handle_loc_lineages = {
        tuple(ancestor.loc for ancestor in leaf.ancestor_iter(inclusive=True))
        for leaf in handle_tree.leaf_node_iter()
    }

    gc_alife_df = tracker.CompilePhylogeny()
    gc_tree = apc.alife_dataframe_to_dendropy_tree(
        gc_alife_df,
        setattrs=["loc"],
    )
    gc_loc_lineages = {
        tuple(ancestor.loc for ancestor in leaf.ancestor_iter(inclusive=True))
        for leaf in gc_tree.leaf_node_iter()
    }

    assert len(handle_tree) == len(gc_tree)
    assert gc_loc_lineages == handle_loc_lineages


def test_GarbateCollectingPhyloTracker_ApplyLocPasteovers():

    # setup population and perfect trackers
    population_size = 10
    common_ancestor = hstrat.PerfectBacktrackHandle(
        data={"loc": 0, "trait": np.nan}
    )
    handle_naivepaste_population = [
        common_ancestor.CreateDescendant(
            data={"loc": loc, "trait": float(loc)}
        )
        for loc in range(population_size)
    ]
    handle_copypaste_population = [
        common_ancestor.CreateDescendant(
            data={"loc": loc, "trait": float(loc)}
        )
        for loc in range(population_size)
    ]
    tracker = hstrat.GarbageCollectingPhyloTracker(
        initial_population=np.arange(population_size),
        working_buffer_size=21,
    )

    # evolve fixed-size population with random selection
    for _generation in range(50):
        _ = _generation
        parent_locs = np.random.randint(population_size, size=population_size)
        tracker.ElapseGeneration(
            parent_locs, traits=np.arange(population_size)
        )
        handle_naivepaste_population = [
            handle_naivepaste_population[parent_loc].CreateDescendant(
                data={"trait": float(loc)}
            )
            for loc, parent_loc in enumerate(parent_locs)
        ]
        handle_copypaste_population = [
            handle_copypaste_population[parent_loc].CreateDescendant(
                data={"trait": float(loc)}
            )
            for loc, parent_loc in enumerate(parent_locs)
        ]

        # apply pasteovers
        copyfrom_locs = np.random.randint(
            population_size, size=np.random.randint(population_size)
        )
        copyto_locs = np.arange(population_size)
        np.random.shuffle(copyto_locs)
        copyto_locs = copyto_locs[: len(copyfrom_locs)]

        tracker.ApplyLocPasteovers(copyfrom_locs, copyto_locs)

        for from_loc, to_loc in zip(copyfrom_locs, copyto_locs):
            handle_naivepaste_population[to_loc] = copy(
                handle_naivepaste_population[from_loc]
            )
            handle_naivepaste_population[to_loc].data = copy(
                handle_naivepaste_population[to_loc].data
            )

        handle_copypaste_population_ = copy(handle_copypaste_population)
        for from_loc, to_loc in zip(copyfrom_locs, copyto_locs):
            handle_copypaste_population[to_loc] = copy(
                handle_copypaste_population_[from_loc]
            )
            handle_copypaste_population[to_loc].data = copy(
                handle_copypaste_population[to_loc].data
            )

        # set loc after pasteovers
        for pop in handle_naivepaste_population, handle_copypaste_population:
            for loc, handle in enumerate(pop):
                handle.data["loc"] = loc

    handle_naivepaste_tree = apc.alife_dataframe_to_dendropy_tree(
        hstrat.compile_perfect_backtrack_phylogeny(
            handle_naivepaste_population
        ),
        setattrs=["loc", "trait"],
    )
    handle_naivepaste_data_lineages = {
        tuple(
            (ancestor.loc, ancestor.trait)
            for ancestor in omit_last(leaf.ancestor_iter(inclusive=True))
        )
        for leaf in handle_naivepaste_tree.leaf_node_iter()
    }

    handle_copypaste_tree = apc.alife_dataframe_to_dendropy_tree(
        hstrat.compile_perfect_backtrack_phylogeny(
            handle_copypaste_population
        ),
        setattrs=["loc", "trait"],
    )
    handle_copypaste_data_lineages = {
        tuple(
            (ancestor.loc, ancestor.trait)
            for ancestor in omit_last(leaf.ancestor_iter(inclusive=True))
        )
        for leaf in handle_copypaste_tree.leaf_node_iter()
    }

    gc_alife_df = tracker.CompilePhylogeny()
    gc_tree = apc.alife_dataframe_to_dendropy_tree(
        gc_alife_df,
        setattrs=["loc", "trait"],
    )
    gc_data_lineages = {
        tuple(
            (ancestor.loc, ancestor.trait)
            for ancestor in omit_last(leaf.ancestor_iter(inclusive=True))
        )
        for leaf in gc_tree.leaf_node_iter()
    }

    assert (
        len(handle_copypaste_tree)
        == len(handle_naivepaste_tree)
        == len(gc_tree)
    )
    assert gc_data_lineages == handle_copypaste_data_lineages
    assert gc_data_lineages != handle_naivepaste_data_lineages

    assert sum(1 for __ in handle_copypaste_tree) == sum(1 for __ in gc_tree)
    assert len(handle_naivepaste_tree) == len(gc_tree)
