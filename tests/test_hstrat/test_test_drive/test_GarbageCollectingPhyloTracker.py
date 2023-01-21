import collections
from copy import copy
import itertools as it

import alifedata_phyloinformatics_convert as apc
import numpy as np
import pandas as pd

from hstrat import hstrat
from hstrat._auxiliary_lib import omit_last


def _compare_compiled_phylogenies(
    control_phylogeny_df: pd.DataFrame,
    test_phylogeny_df: pd.DataFrame,
) -> None:
    # compile tree tracked with handle tracker
    control_tree = apc.alife_dataframe_to_dendropy_tree(
        control_phylogeny_df,
    )

    # compile tree tracked with gc tracker
    assert len(test_phylogeny_df) == len(test_phylogeny_df["id"].unique())
    test_tree = apc.alife_dataframe_to_dendropy_tree(
        test_phylogeny_df,
    )
    assert sum(1 for __ in test_tree.leaf_node_iter()) == sum(
        1 for __ in control_tree.leaf_node_iter()
    )
    assert len(set(node.level() for node in test_tree.leaf_node_iter())) == 1

    # setup taxa in both trees
    for tree in test_tree, control_tree:
        for i, n in enumerate(tree):
            n.taxon = tree.taxon_namespace.new_taxon(f"{i}")

    # check phylogenetic trees tracked in different ways are identical
    assert collections.Counter(
        node.level() for node in control_tree
    ) == collections.Counter(node.level() for node in test_tree)
    assert collections.Counter(
        control_tree.mrca(taxa=[n1.taxon, n2.taxon]).level()
        for n1, n2 in it.combinations(control_tree.leaf_node_iter(), 2)
    ) == collections.Counter(
        test_tree.mrca(taxa=[n1.taxon, n2.taxon]).level()
        for n1, n2 in it.combinations(test_tree.leaf_node_iter(), 2)
    )


def test_GarbateCollectingPhyloTracker():

    # setup population and perfect trackers
    population_size = 20
    common_ancestor = hstrat.PerfectBacktrackHandle()
    handle_population = [
        common_ancestor.CreateDescendant() for __ in range(population_size)
    ]
    tracker = hstrat.GarbageCollectingPhyloTracker(
        initial_population=population_size,
        working_buffer_size=21,
    )

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


def test_GarbateCollectingPhyloTracker_ApplyLocSwaps():

    # setup population and perfect trackers
    population_size = 4
    common_ancestor = hstrat.PerfectBacktrackHandle(data=0)
    handle_population = [
        common_ancestor.CreateDescendant(data=idx)
        for idx in range(population_size)
    ]
    tracker = hstrat.GarbageCollectingPhyloTracker(
        initial_population=population_size,
        working_buffer_size=21,
    )

    # evolve fixed-size population with random selection
    for generation in range(50):
        parent_idxs = np.random.randint(population_size, size=population_size)
        tracker.ElapseGeneration(parent_idxs)
        handle_population = [
            handle_population[idx].CreateDescendant() for idx in parent_idxs
        ]

        swapfrom_idxs = np.random.randint(
            population_size, size=population_size
        )
        swapto_idxs = np.random.randint(population_size, size=population_size)

        tracker.ApplyLocSwaps(swapfrom_idxs, swapto_idxs)
        for from_idx, to_idx in zip(swapfrom_idxs, swapto_idxs):
            handle_population[from_idx], handle_population[to_idx] = (
                handle_population[to_idx],
                handle_population[from_idx],
            )

        for idx, handle in enumerate(handle_population):
            handle.data = idx

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
            data={"loc": idx, "trait": float(idx)}
        )
        for idx in range(population_size)
    ]
    handle_copypaste_population = [
        common_ancestor.CreateDescendant(
            data={"loc": idx, "trait": float(idx)}
        )
        for idx in range(population_size)
    ]
    tracker = hstrat.GarbageCollectingPhyloTracker(
        initial_population=np.arange(population_size),
        working_buffer_size=21,
    )

    # evolve fixed-size population with random selection
    for generation in range(50):
        parent_idxs = np.random.randint(population_size, size=population_size)
        tracker.ElapseGeneration(
            parent_idxs, traits=np.arange(len(parent_idxs))
        )
        handle_naivepaste_population = [
            handle_naivepaste_population[idx].CreateDescendant(
                data={"trait": float(loc)}
            )
            for loc, idx in enumerate(parent_idxs)
        ]
        handle_copypaste_population = [
            handle_copypaste_population[idx].CreateDescendant(
                data={"trait": float(loc)}
            )
            for loc, idx in enumerate(parent_idxs)
        ]

        # apply pasteovers
        copyfrom_idxs = np.random.randint(
            population_size, size=np.random.randint(population_size)
        )
        copyto_idxs = np.arange(population_size)
        np.random.shuffle(copyto_idxs)
        copyto_idxs = copyto_idxs[: len(copyfrom_idxs)]

        tracker.ApplyLocPasteovers(copyfrom_idxs, copyto_idxs)

        for from_idx, to_idx in zip(copyfrom_idxs, copyto_idxs):
            handle_naivepaste_population[to_idx] = copy(
                handle_naivepaste_population[from_idx]
            )
            handle_naivepaste_population[to_idx].data = copy(
                handle_naivepaste_population[to_idx].data
            )

        handle_copypaste_population_ = copy(handle_copypaste_population)
        for from_idx, to_idx in zip(copyfrom_idxs, copyto_idxs):
            handle_copypaste_population[to_idx] = copy(
                handle_copypaste_population_[from_idx]
            )
            handle_copypaste_population[to_idx].data = copy(
                handle_copypaste_population[to_idx].data
            )

        # set loc after pasteovers
        for pop in handle_naivepaste_population, handle_copypaste_population:
            for idx, handle in enumerate(pop):
                handle.data["loc"] = idx

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