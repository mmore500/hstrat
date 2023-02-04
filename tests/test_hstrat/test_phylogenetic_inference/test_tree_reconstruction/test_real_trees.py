from hstrat import hstrat
from hstrat.phylogenetic_inference import tree_reconstruction

import itertools
import opytional as opyt

from alifedata_phyloinformatics_convert import dendropy_tree_to_alife_dataframe, biopython_tree_to_alife_dataframe, alife_dataframe_to_dendropy_tree

import pandas as pd

from aux_tree_tools import tree_distance_metric, AuxTree

import dendropy as dp
import os

import pytest

assets_path = os.path.join(os.path.dirname(__file__), "assets")

def load_dendropy_tree(path):
    if path.endswith(".csv"):
        return AuxTree(pd.read_csv(path)).dendropy
    elif path.endswith(".newick"):
        return dp.Tree.get(path=path, schema="newick")

def setup_dendropy_tree(path):
    tree = load_dendropy_tree(path)

    for node in tree:
        node.edge.length = 1

    for idx, node in enumerate(tree.leaf_node_iter()):
        node.taxon = tree.taxon_namespace.new_taxon(label=str(idx))

    tree.update_bipartitions(
        suppress_unifurcations=False,
        collapse_unrooted_basal_bifurcation=False,
    )

    return tree

def descend_unifurcations(node):
    while len(node.child_nodes()) == 1:
        node = next(node.child_node_iter())
    return node

def descent_extant_population(tree, retention_policy, num_depositions):
    seed_column = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=retention_policy,
    )

    seed_column.DepositStrata(num_stratum_depositions=num_depositions)

    return hstrat.descend_template_phylogeny(
        ascending_lineage_iterators=(
            tip_node.ancestor_iter(
                inclusive=True,
            )
            for tip_node in tree.leaf_node_iter()
        ),
        descending_tree_iterator=tree.levelorder_node_iter(),
        get_parent=lambda node: node.parent_node,
        get_stem_length=lambda node: node.edge_length,
        seed_column=seed_column,
    )

@pytest.mark.parametrize(
    "path",
    [
        f"{assets_path}/nk_ecoeaselection.csv",
        f"{assets_path}/nk_lexicaseselection.csv",
        f"{assets_path}/nk_tournamentselection.csv",
        f"{assets_path}/grandchild_and_aunt.newick",
        f"{assets_path}/grandchild_and_auntuncle.newick",
        f"{assets_path}/grandtriplets_and_aunt.newick",
        f"{assets_path}/grandtriplets_and_auntuncle.newick",
        f"{assets_path}/grandtriplets.newick",
        f"{assets_path}/grandtwins_and_aunt.newick",
        f"{assets_path}/grandtwins_and_auntuncle.newick",
        f"{assets_path}/grandtwins.newick",
        f"{assets_path}/triplets.newick",
        f"{assets_path}/twins.newick",
    ],
)
def test_print_performance(path):
    orig_tree = setup_dendropy_tree(path)

    extant_population = descent_extant_population(
        tree=orig_tree,
        retention_policy=hstrat.perfect_resolution_algo.Policy(),
        num_depositions=10
    )

    distance_matrix = tree_reconstruction.calculate_distance_matrix(extant_population)
    reconstructed_tree = tree_reconstruction.reconstruct_tree(distance_matrix)

    print(path)
    print(
        orig_tree.as_ascii_plot(
            show_internal_node_labels=True,
            leaf_spacing_factor=1
        ),
        end="\r"
    )
    print(f"metric={tree_distance_metric(orig_tree, reconstructed_tree)}")
    print()

@pytest.mark.parametrize(
    "path",
    [
        f"{assets_path}/grandchild_and_aunt.newick"
        f"{assets_path}/grandchild_and_auntuncle.newick",
        # TODO: handle this edge case
        # f"{assets_path}/grandchild.newick",
        f"{assets_path}/grandtriplets_and_aunt.newick",
        f"{assets_path}/grandtriplets_and_auntuncle.newick",
        f"{assets_path}/grandtriplets.newick"
        f"{assets_path}/grandtwins_and_aunt.newick"
        f"{assets_path}/grandtwins_and_auntuncle.newick",
        f"{assets_path}/grandtwins.newick"
        # TODO: handle this edge case
        # f"{assets_path}/justroot.newick"
        f"{assets_path}/triplets.newick"
        f"{assets_path}/twins.newick"
    ],
)
def test_handwritten_trees(path):
    orig_tree = setup_dendropy_tree(path)

    extant_population = descent_extant_population(
        tree=orig_tree,
        retention_policy=hstrat.perfect_resolution_algo.Policy(),
        num_depositions=10
    )

    distance_matrix = tree_reconstruction.calculate_distance_matrix(extant_population)
    reconstructed_tree = tree_reconstruction.reconstruct_tree(distance_matrix)

    rec = AuxTree(reconstructed_tree).dendropy
    rec.collapse_unweighted_edges()

    common_namespace = dp.TaxonNamespace()
    orig_tree.migrate_taxon_namespace(common_namespace)
    rec.migrate_taxon_namespace(common_namespace)

    original_distance_matrix = orig_tree.phylogenetic_distance_matrix()
    reconstructed_distance_matrix = rec.phylogenetic_distance_matrix()

    taxa = [node.taxon for node in orig_tree.leaf_node_iter()]

    for a, b in itertools.combinations(taxa, 2):
        assert abs(original_distance_matrix.distance(a, b) - reconstructed_distance_matrix.distance(a, b)) < 2.0

    assert tree_distance_metric(
        orig_tree,
        reconstructed_tree
    ) < 2.0

@pytest.mark.parametrize(
    "path",
    [
        f"{assets_path}/nk_ecoeaselection.csv",
        # f"{assets_path}/nk_lexicaseselection.csv",
        # f"{assets_path}/nk_tournamentselection.csv",
    ],
)
def test_realworld_trees(path):
    orig_tree = setup_dendropy_tree(path)

    extant_population = descent_extant_population(
        tree=orig_tree,
        retention_policy=hstrat.perfect_resolution_algo.Policy(),
        num_depositions=10
    )

    distance_matrix = tree_reconstruction.calculate_distance_matrix(extant_population)
    reconstructed_tree = tree_reconstruction.reconstruct_tree(distance_matrix)

    rec = AuxTree(reconstructed_tree).dendropy
    rec.collapse_unweighted_edges()

    common_namespace = dp.TaxonNamespace()
    orig_tree.migrate_taxon_namespace(common_namespace)
    rec.migrate_taxon_namespace(common_namespace)

    original_distance_matrix = orig_tree.phylogenetic_distance_matrix()
    reconstructed_distance_matrix = rec.phylogenetic_distance_matrix()

    taxa = [node.taxon for node in orig_tree.leaf_node_iter()]

    # TODO: only check that 95% of these are good enough
    for a, b in itertools.combinations(taxa, 2):
        assert abs(original_distance_matrix.distance(a, b) - reconstructed_distance_matrix.distance(a, b)) < 100.0

    assert tree_distance_metric(
        orig_tree,
        reconstructed_tree
    ) < 1000.0


@pytest.mark.parametrize(
    "path",
    [
        f"{assets_path}/grandchild_and_aunt.newick",
        f"{assets_path}/grandchild_and_auntuncle.newick",
        # TODO: handle this edge case
        # dp.Tree.get(path=f"{assets_path}/grandchild.newick",
        f"{assets_path}/grandtriplets_and_aunt.newick",
        f"{assets_path}/grandtriplets_and_auntuncle.newick",
        f"{assets_path}/grandtriplets.newick",
        f"{assets_path}/grandtwins_and_aunt.newick",
        f"{assets_path}/grandtwins_and_auntuncle.newick",
        f"{assets_path}/grandtwins.newick",
        # TODO: handle this edge case
        # dp.Tree.get(path=f"{assets_path}/justroot.newick",
        f"{assets_path}/triplets.newick",
        f"{assets_path}/twins.newick",
        f"{assets_path}/nk_ecoeaselection.csv",
        f"{assets_path}/nk_lexicaseselection.csv",
        f"{assets_path}/nk_tournamentselection.csv",
    ],
)
def test_reconstruction_quality(path):
    orig_tree = setup_dendropy_tree(path)

    resolutions = [1, 10, 100, 1000]
    metrics = []

    for resolution in resolutions:
        extant_population = descent_extant_population(
            tree=orig_tree,
            retention_policy=hstrat.fixed_resolution_algo.Policy(resolution),
            num_depositions=10
        )

        distance_matrix = tree_reconstruction.calculate_distance_matrix(extant_population)
        reconstructed_tree = tree_reconstruction.reconstruct_tree(distance_matrix)

        metrics.append(tree_distance_metric(
            orig_tree,
            reconstructed_tree
        ))

    # make sure tree distances are increasing with resolution
    assert resolutions == sorted(resolutions)
    assert metrics == sorted(metrics)


@pytest.mark.parametrize(
    "path",
    [
        # f"{assets_path}/nk_ecoeaselection.csv",
        f"{assets_path}/nk_lexicaseselection.csv",
        f"{assets_path}/nk_tournamentselection.csv",
    ],
)
def test_reconstructed_mrca(path):
    num_depositions = 10
    threshold = 0.99

    orig_tree = setup_dendropy_tree(path)

    extant_population = descent_extant_population(
        tree=orig_tree,
        retention_policy=hstrat.perfect_resolution_algo.Policy(),
        num_depositions=num_depositions,
    )

    pdm = orig_tree.phylogenetic_distance_matrix()

    assert len(list(orig_tree.leaf_node_iter())) == len(extant_population)
    assert [x.distance_from_root() + num_depositions for x in orig_tree.leaf_node_iter()] == \
        [x._num_strata_deposited for x in extant_population]

    for orig_pair, rec_pair in zip(
        itertools.combinations(orig_tree.leaf_node_iter(), 2),
        itertools.combinations(extant_population, 2)
    ):
        original_mrca = descend_unifurcations(pdm.mrca(*map(lambda x: x.taxon, orig_pair)))

        lower_mrca_bound, upper_mrca_bound = hstrat.calc_rank_of_mrca_bounds_between(*rec_pair)

        assert threshold * (lower_mrca_bound - num_depositions) <= original_mrca.distance_from_root()
        assert original_mrca.distance_from_root() < (upper_mrca_bound - num_depositions) * (2 - threshold)
