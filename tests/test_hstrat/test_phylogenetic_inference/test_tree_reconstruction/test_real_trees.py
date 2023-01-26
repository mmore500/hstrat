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
    orig_tree = load_dendropy_tree(path)

    for node in orig_tree:
        node.edge.length = 1

    for idx, node in enumerate(orig_tree.leaf_node_iter()):
        node.taxon = orig_tree.taxon_namespace.new_taxon(label=str(idx))

    orig_tree.update_bipartitions(
        suppress_unifurcations=False,
        collapse_unrooted_basal_bifurcation=False,
    )

    seed_column = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=hstrat.perfect_resolution_algo.Policy(
        ),
    )
    seed_column.DepositStrata(num_stratum_depositions=10)

    extant_population = hstrat.descend_template_phylogeny(
        ascending_lineage_iterators=(
            tip_node.ancestor_iter(
                inclusive=True,
            )
            for tip_node in orig_tree.leaf_node_iter()
        ),
        descending_tree_iterator=orig_tree.levelorder_node_iter(),
        get_parent=lambda node: node.parent_node,
        get_stem_length=lambda node: node.edge_length,
        seed_column=seed_column,
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
    orig_tree = load_dendropy_tree(path)

    for node in orig_tree:
        node.edge.length = 1

    for idx, node in enumerate(orig_tree.leaf_node_iter()):
        node.taxon = orig_tree.taxon_namespace.new_taxon(label=str(idx))

    orig_tree.update_bipartitions(
        suppress_unifurcations=False,
        collapse_unrooted_basal_bifurcation=False,
    )

    seed_column = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=hstrat.perfect_resolution_algo.Policy(
        ),
    )
    seed_column.DepositStrata(num_stratum_depositions=10)

    extant_population = hstrat.descend_template_phylogeny(
        ascending_lineage_iterators=(
            tip_node.ancestor_iter(
                inclusive=True,
            )
            for tip_node in orig_tree.leaf_node_iter()
        ),
        descending_tree_iterator=orig_tree.levelorder_node_iter(),
        get_parent=lambda node: node.parent_node,
        get_stem_length=lambda node: node.edge_length,
        seed_column=seed_column,
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
        f"{assets_path}/nk_lexicaseselection.csv",
        f"{assets_path}/nk_tournamentselection.csv",
    ],
)
def test_realworld_trees(path):
    orig_tree = load_dendropy_tree(path)

    for node in orig_tree:
        node.edge_length = 1

    for idx, node in enumerate(orig_tree.leaf_node_iter()):
        node.taxon = orig_tree.taxon_namespace.new_taxon(label=str(idx))

    orig_tree.update_bipartitions(
        suppress_unifurcations=False,
        collapse_unrooted_basal_bifurcation=False,
    )

    seed_column = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=hstrat.perfect_resolution_algo.Policy(
        ),
    )
    seed_column.DepositStrata(num_stratum_depositions=10)

    extant_population = hstrat.descend_template_phylogeny(
        ascending_lineage_iterators=(
            tip_node.ancestor_iter(
                inclusive=True,
            )
            for tip_node in orig_tree.leaf_node_iter()
        ),
        descending_tree_iterator=orig_tree.levelorder_node_iter(),
        get_parent=lambda node: node.parent_node,
        get_stem_length=lambda node: node.edge_length,
        seed_column=seed_column,
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
    orig_tree = load_dendropy_tree(path)

    for node in orig_tree:
        node.edge_length = 1

    for idx, node in enumerate(orig_tree.leaf_node_iter()):
        node.taxon = orig_tree.taxon_namespace.new_taxon(label=str(idx))

    orig_tree.update_bipartitions(
        suppress_unifurcations=False,
        collapse_unrooted_basal_bifurcation=False,
    )

    resolutions = [1, 10, 100, 1000]
    metrics = []

    for resolution in resolutions:
        seed_column = hstrat.HereditaryStratigraphicColumn(
            stratum_retention_policy=hstrat.fixed_resolution_algo.Policy(resolution),
        )
        seed_column.DepositStrata(num_stratum_depositions=10)

        extant_population = hstrat.descend_template_phylogeny(
            ascending_lineage_iterators=(
                tip_node.ancestor_iter(
                    inclusive=True,
                )
                for tip_node in orig_tree.leaf_node_iter()
            ),
            descending_tree_iterator=orig_tree.levelorder_node_iter(),
            get_parent=lambda node: node.parent_node,
            get_stem_length=lambda node: node.edge_length,
            seed_column=seed_column,
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
    orig_tree = load_dendropy_tree(path)

    for node in orig_tree:
        node.edge_length = 1

    for idx, node in enumerate(orig_tree.leaf_node_iter()):
        node.taxon = orig_tree.taxon_namespace.new_taxon(label=str(idx))

    orig_tree.update_bipartitions(
        suppress_unifurcations=False,
        collapse_unrooted_basal_bifurcation=False,
    )

    seed_column = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=hstrat.perfect_resolution_algo.Policy(),
    )
    seed_column.DepositStrata(num_stratum_depositions=10)

    extant_population = hstrat.descend_template_phylogeny(
        ascending_lineage_iterators=(
            tip_node.ancestor_iter(
                inclusive=True,
            )
            for tip_node in orig_tree.leaf_node_iter()
        ),
        descending_tree_iterator=orig_tree.levelorder_node_iter(),
        get_parent=lambda node: node.parent_node,
        get_stem_length=lambda node: node.edge_length,
        seed_column=seed_column,
    )

    threshold = 0.9

    for orig_pair, rec_pair in zip(
        itertools.combinations(orig_tree.leaf_node_iter(), 2),
        itertools.combinations(extant_population, 2)
    ):
        pdm = orig_tree.phylogenetic_distance_matrix()
        original_mrca = pdm.mrca(*map(lambda x: x.taxon, orig_pair))
        lower_mrca_bound, upper_mrca_bound = hstrat.calc_rank_of_mrca_bounds_between(*rec_pair)

        assert threshold * lower_mrca_bound <= original_mrca.distance_from_root()
        assert original_mrca.distance_from_root() < upper_mrca_bound * (2 - threshold)
