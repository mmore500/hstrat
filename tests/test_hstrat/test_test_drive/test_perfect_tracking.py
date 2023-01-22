import itertools as it
import os

import alifedata_phyloinformatics_convert as apc
import dendropy as dp
import pandas as pd
import pytest

from hstrat import hstrat
from hstrat._auxiliary_lib import pairwise, zip_strict

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize(
    "tree",
    [
        dp.Tree(),
        dp.Tree.get(
            path=f"{assets_path}/grandchild_and_aunt.newick", schema="newick"
        ),
        dp.Tree.get(
            path=f"{assets_path}/grandchild_and_auntuncle.newick",
            schema="newick",
        ),
        dp.Tree.get(path=f"{assets_path}/grandchild.newick", schema="newick"),
        dp.Tree.get(
            path=f"{assets_path}/grandtriplets_and_aunt.newick",
            schema="newick",
        ),
        dp.Tree.get(
            path=f"{assets_path}/grandtriplets_and_auntuncle.newick",
            schema="newick",
        ),
        dp.Tree.get(
            path=f"{assets_path}/grandtriplets.newick", schema="newick"
        ),
        dp.Tree.get(
            path=f"{assets_path}/grandtwins_and_aunt.newick", schema="newick"
        ),
        dp.Tree.get(
            path=f"{assets_path}/grandtwins_and_auntuncle.newick",
            schema="newick",
        ),
        dp.Tree.get(path=f"{assets_path}/grandtwins.newick", schema="newick"),
        dp.Tree.get(path=f"{assets_path}/justroot.newick", schema="newick"),
        dp.Tree.get(path=f"{assets_path}/triplets.newick", schema="newick"),
        dp.Tree.get(path=f"{assets_path}/twins.newick", schema="newick"),
        apc.alife_dataframe_to_dendropy_tree(
            pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        ),
        apc.alife_dataframe_to_dendropy_tree(
            pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        ),
        apc.alife_dataframe_to_dendropy_tree(
            pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
        ),
    ],
)
def test_perfect_tracking(tree):

    # setup tree
    for loc, node in enumerate(tree):
        node.taxon = tree.taxon_namespace.new_taxon(label=str(loc))

    tree.update_bipartitions(
        suppress_unifurcations=False,
        collapse_unrooted_basal_bifurcation=False,
    )

    handle_population = [
        hstrat.PerfectBacktrackHandle(
            data={
                "taxon_label": tree.seed_node.taxon.label,
            },
        )
    ]
    for (
        (ancestor_level, ancestor_level_nodes),
        (descendant_level, descendant_level_nodes),
    ) in pairwise(
        (
            (level, [*group])
            for level, group in it.groupby(
                tree.levelorder_node_iter(),
                lambda node: node.level(),
            )
        )
    ):
        ancestor_handle_lookup = {
            id(ancestor_node): ancestor_handle
            for (ancestor_node, ancestor_handle) in zip_strict(
                ancestor_level_nodes, handle_population
            )
        }

        handle_population = [
            ancestor_handle_lookup[
                id(descendant_node.parent_node)
            ].CreateDescendant(
                data={"taxon_label": descendant_node.taxon.label},
            )
            for descendant_node in descendant_level_nodes
        ]

    alifedata_df = hstrat.compile_perfect_backtrack_phylogeny(
        handle_population,
    )
    assert len(alifedata_df) <= sum(1 for __ in tree)
    assert len(alifedata_df) == len(alifedata_df["id"].unique())

    tracked_tree = apc.alife_dataframe_to_dendropy_tree(
        alifedata_df,
    )

    max_level = max((node.level() for node in tree.leaf_node_iter()))
    extant_subtree = tree.extract_tree(
        node_filter_fn=lambda node: node.level() == max_level
    )
    assert len(tracked_tree) == len(extant_subtree)
    assert len(extant_subtree)

    tracked_tree.migrate_taxon_namespace(extant_subtree.taxon_namespace)
    assert tracked_tree.taxon_namespace is extant_subtree.taxon_namespace
    for node in tracked_tree:
        assert node.taxon in extant_subtree.taxon_namespace

    assert (
        dp.calculate.treecompare.symmetric_difference(
            extant_subtree,
            tracked_tree,
            is_bipartitions_updated=True,
        )
        == 0
    )
