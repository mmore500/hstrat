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
        hstrat.stochastic_algo.Policy(retention_probability=0.05),
        hstrat.depth_proportional_resolution_algo.Policy(
            depth_proportional_resolution=10
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
def test_descend_template_phylogeny(
    always_store_rank_in_stratum,
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

    extant_population = hstrat.descend_template_phylogeny_dendropy(
        tree,
        seed_column=seed_column,
    )

    num_tips = len(tree)
    assert num_tips == len(extant_population)

    tip_depths = [
        int(tip_node.distance_from_root())
        for tip_node in tree.leaf_node_iter()
    ]
    assert tip_depths == [
        column.GetNumStrataDeposited() - 1 for column in extant_population
    ]

    sampled_product = it.permutations(
        random.sample(
            [*zip(extant_population, tree.leaf_node_iter())],
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
        mrca = tree.mrca(
            taxa=[n1.taxon, n2.taxon],
            is_bipartitions_updated=True,
        )
        # patch for dendropy bug where internal unifurcations are not accounted
        # for in mrca detection
        # see https://github.com/jeetsukumaran/DendroPy/pull/148
        while mrca.num_child_nodes() == 1:
            (mrca,) = mrca.child_nodes()

        assert lb <= mrca.distance_from_root() < ub


@pytest.mark.parametrize(
    "always_store_rank_in_stratum",
    [
        True,
        False,
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
        hstrat.stochastic_algo.Policy(retention_probability=0.05),
        hstrat.depth_proportional_resolution_algo.Policy(
            depth_proportional_resolution=10
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
def test_descend_template_phylogeny_extant_ids(
    always_store_rank_in_stratum,
    num_predeposits,
    retention_policy,
    set_stem_length,
    tree,
):
    # setup tree
    for node in tree:
        node.edge_length = set_stem_length(node)

    tree.seed_node.edge_length = num_predeposits

    for loc, node in enumerate(tree):
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

    node_list = [*tree]
    extant_nodes = random.sample(node_list, random.randrange(len(node_list)))

    extant_population = hstrat.descend_template_phylogeny_dendropy(
        tree,
        seed_column=seed_column,
        extant_nodes=extant_nodes,
        progress_wrap=functools.partial(tqdm, disable=True),
    )

    num_extants = len(extant_nodes)
    assert num_extants == len(extant_population)

    extant_depths = [
        int(extant_node.distance_from_root()) for extant_node in extant_nodes
    ]
    assert extant_depths == [
        column.GetNumStrataDeposited() - 1 for column in extant_population
    ]

    sampled_product = it.permutations(
        random.sample(
            [*zip(extant_population, extant_nodes)],
            min(10, len(extant_population)),
        ),
        2,
    )
    spliced_product = it.permutations(
        it.islice(zip(extant_population, extant_nodes), 10),
        2,
    )

    for (c1, n1), (c2, n2) in it.chain(sampled_product, spliced_product):
        lb, ub = hstrat.calc_rank_of_mrca_bounds_between(
            c1, c2, prior="arbitrary"
        )
        assert n1 != n2
        if n1 in n2.ancestor_iter():
            mrca = n1
        elif n2 in n1.ancestor_iter():
            mrca = n2
        else:

            # dendropy mrca lookup requires leaf nodes
            while n1.num_child_nodes():
                n1, *__ = n1.child_nodes()
            while n2.num_child_nodes():
                n2, *__ = n2.child_nodes()

            mrca = tree.mrca(
                taxa=[n1.taxon, n2.taxon],
                is_bipartitions_updated=True,
            )
            # patch for dendropy bug where internal unifurcations are not
            # accounted for in mrca detection
            # see https://github.com/jeetsukumaran/DendroPy/pull/148
            while mrca.num_child_nodes() == 1:
                (mrca,) = mrca.child_nodes()

        assert lb <= mrca.distance_from_root() < ub
