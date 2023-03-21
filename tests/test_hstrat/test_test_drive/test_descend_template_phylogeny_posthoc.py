import functools
import itertools as it
import os
import random

import alifedata_phyloinformatics_convert as apc
import dendropy as dp
import pandas as pd
import pytest
from tqdm import tqdm

from hstrat import hstrat

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize(
    "always_store_rank_in_stratum",
    [
        True,
        False,
    ],
)
@pytest.mark.parametrize(
    "iter_extant_nodes",
    [
        # just extants
        lambda tree: tree.leaf_node_iter(),
        # with internal nodes
        lambda tree: it.chain(
            tree.leaf_node_iter(),
            # note: will yield duplicates of internal nodes
            (
                leaf_node.parent_node
                for leaf_node in tree.leaf_node_iter()
                if leaf_node.parent_node is not None
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    "num_predeposits",
    [
        0,
        1,
        10,
        100,
    ],
)
@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.depth_proportional_resolution_algo.Policy(
            depth_proportional_resolution=10
        ),
        pytest.param(
            hstrat.depth_proportional_resolution_algo.Policy(
                depth_proportional_resolution=100
            ),
            marks=pytest.mark.heavy_3a,
        ),
        pytest.param(
            hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
            marks=pytest.mark.heavy_3a,
        ),
        hstrat.recency_proportional_resolution_algo.Policy(
            recency_proportional_resolution=2
        ),
    ],
)
@pytest.mark.parametrize(
    "set_stem_length",
    [
        lambda node: 1,
        lambda node: 1 + random.randrange(10),
        pytest.param(
            lambda node: 1 + random.randrange(100),
            marks=pytest.mark.heavy_3b,
        ),
    ],
)
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
        pytest.param(
            apc.alife_dataframe_to_dendropy_tree(
                pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
            ),
            marks=pytest.mark.heavy_3c,
        ),
        apc.alife_dataframe_to_dendropy_tree(
            pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        ),
        apc.alife_dataframe_to_dendropy_tree(
            pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
        ),
    ],
)
def test_descend_template_phylogeny_posthoc(
    always_store_rank_in_stratum,
    iter_extant_nodes,
    num_predeposits,
    retention_policy,
    set_stem_length,
    tree,
):
    # setup tree
    for node in tree:
        node.edge_length = set_stem_length(node)

    tree.seed_node.edge_length = num_predeposits

    for loc, node in enumerate(tree.leaf_node_iter()):
        node.taxon = tree.taxon_namespace.new_taxon(label=str(loc))

    tree.update_bipartitions(
        suppress_unifurcations=False,
        collapse_unrooted_basal_bifurcation=False,
    )

    # setup seed column
    seed_column = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=retention_policy,
        always_store_rank_in_stratum=always_store_rank_in_stratum,
    )
    seed_column.DepositStrata(num_stratum_depositions=num_predeposits)

    extant_population = hstrat.descend_template_phylogeny_posthoc(
        ascending_lineage_iterables=(
            extant_node.ancestor_iter(
                inclusive=True,
            )
            for extant_node in iter_extant_nodes(tree)
        ),
        descending_tree_iterable=tree.levelorder_node_iter(),
        get_parent=lambda node: node.parent_node,
        get_stem_length=lambda node: node.edge_length,
        seed_column=seed_column,
        progress_wrap=functools.partial(tqdm, disable=True),
    )

    num_extants = sum(1 for __ in iter_extant_nodes(tree))
    assert num_extants == len(extant_population)

    extant_depths = [
        int(extant_node.distance_from_root())
        for extant_node in iter_extant_nodes(tree)
    ]
    assert extant_depths == [
        column.GetNumStrataDeposited() - 1 for column in extant_population
    ]

    assert all(
        column.GetNumStrataRetained()
        == column._stratum_retention_policy.CalcNumStrataRetainedExact(
            column.GetNumStrataDeposited()
        )
        for column in extant_population
    )
    assert all(
        a == b
        for column in extant_population
        for a, b in zip(
            column.IterRetainedRanks(),
            column._stratum_retention_policy.IterRetainedRanks(
                column.GetNumStrataDeposited()
            ),
        )
    )

    sampled_product = it.permutations(
        random.sample(
            [*zip(extant_population, iter_extant_nodes(tree))],
            min(10, len(extant_population)),
        ),
        2,
    )
    spliced_product = it.permutations(
        it.islice(zip(extant_population, tree.leaf_node_iter()), 10),
        2,
    )

    for (c1, n1), (c2, n2) in it.chain(sampled_product, spliced_product):
        lb, ub = hstrat.calc_rank_of_mrca_bounds_between(
            c1, c2, prior="arbitrary"
        )
        if n1 == n2:
            mrca = n1
        elif n1.parent_node == n2:
            mrca = n2
        elif n2.parent_node == n1:
            mrca = n1
        else:
            # convert any internal nodes to mrca-equivalent leaf nodes
            for candidate in n1.child_nodes():
                if candidate not in n2.ancestor_iter():
                    n1 = candidate

            while n1.num_child_nodes():
                n1 = n1.child_nodes()[0]

            for candidate in n2.child_nodes():
                if candidate not in n1.ancestor_iter():
                    n2 = candidate

            while n2.num_child_nodes():
                n2 = n2.child_nodes()[0]

            mrca = tree.mrca(
                taxa=[n1.taxon, n2.taxon],
                is_bipartitions_updated=True,
            )
            # patch for dendropy bug where internal unifurcations are not accounted
            # for in mrca detection
            # see https://github.com/jeetsukumaran/DendroPy/pull/148
            while mrca.num_child_nodes() == 1:
                (mrca,) = mrca.child_nodes()

        if not lb <= mrca.distance_from_root() < ub:
            print(mrca)
            print(n1, n1.child_nodes())
            print(n2, n2.child_nodes())
        assert lb <= mrca.distance_from_root() < ub
