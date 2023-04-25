from collections import Counter
import functools
import itertools as it
import os
import random

from Bio import Phylo as BioPhylo
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
        hstrat.pseudostochastic_algo.Policy(hash_salt=3),
        hstrat.depth_proportional_resolution_algo.Policy(
            depth_proportional_resolution=10
        ),
        hstrat.recency_proportional_resolution_algo.Policy(
            recency_proportional_resolution=2
        ),
    ],
)
@pytest.mark.parametrize(
    "tree_path",
    [
        "",
        f"{assets_path}/grandchild_and_aunt.newick",
        f"{assets_path}/grandchild_and_auntuncle.newick",
        f"{assets_path}/grandchild.newick",
        f"{assets_path}/grandtriplets_and_aunt.newick",
        f"{assets_path}/grandtriplets_and_auntuncle.newick",
        f"{assets_path}/grandtriplets.newick",
        f"{assets_path}/grandtwins_and_aunt.newick",
        f"{assets_path}/grandtwins_and_auntuncle.newick",
        f"{assets_path}/grandtwins.newick",
        f"{assets_path}/justroot.newick",
        f"{assets_path}/triplets.newick",
        f"{assets_path}/twins.newick",
        f"{assets_path}/nk_tournamentselection.csv",
    ],
)
def test_descend_template_phylogeny(
    always_store_rank_in_stratum,
    num_predeposits,
    retention_policy,
    tree_path,
):

    if tree_path == "":
        tree = dp.Tree()
        bp_tree = BioPhylo.BaseTree.Tree()
    elif tree_path.endswith(".newick"):
        tree = dp.Tree.get(path=tree_path, schema="newick")
        bp_tree = BioPhylo.read(tree_path, "newick")
    elif tree_path.endswith(".csv"):
        tree = apc.alife_dataframe_to_dendropy_tree(
            pd.read_csv(tree_path),
        )
        bp_tree = apc.alife_dataframe_to_biopython_tree(
            pd.read_csv(tree_path),
        )
    else:
        assert False

    for node in tree:
        node.edge_length = 1
    for clade in bp_tree.find_clades():
        clade.branch_length = 1
    tree.seed_node.edge.length = num_predeposits
    bp_tree.rooted = True
    bp_tree.root.branch_length = num_predeposits

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
        stratum_differentia_bit_width=64,
    )
    seed_column.DepositStrata(num_stratum_depositions=num_predeposits)

    extant_population = hstrat.descend_template_phylogeny_biopython(
        bp_tree,
        seed_column=seed_column,
        progress_wrap=functools.partial(tqdm, disable=True),
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

    extant_population_dp = hstrat.descend_template_phylogeny_dendropy(
        tree,
        seed_column=seed_column,
        progress_wrap=functools.partial(tqdm, disable=True),
    )

    assert len(extant_population) == len(extant_population_dp)

    assert Counter(
        hstrat.calc_rank_of_mrca_bounds_between(c1, c2, prior="arbitrary")
        for c1, c2 in it.permutations(extant_population, 2)
    ) == Counter(
        hstrat.calc_rank_of_mrca_bounds_between(c1, c2, prior="arbitrary")
        for c1, c2 in it.permutations(extant_population_dp, 2)
    )

    extant_nodes = random.sample(
        [*bp_tree.find_clades()], min(2, len([*bp_tree.find_clades()]))
    )
    extant_population = hstrat.descend_template_phylogeny_biopython(
        bp_tree,
        seed_column=seed_column,
        extant_nodes=extant_nodes,
        progress_wrap=functools.partial(tqdm, disable=True),
    )
    assert len(extant_nodes) == len(extant_population)

    depths = bp_tree.depths()
    assert Counter(depths[n] for n in extant_nodes) == Counter(
        c.GetNumStrataDeposited() - 1 for c in extant_population
    )
