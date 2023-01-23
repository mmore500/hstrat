from hstrat import hstrat
from hstrat.phylogenetic_inference import tree_reconstruction

import itertools
import opytional as opyt

from alifedata_phyloinformatics_convert import dendropy_tree_to_alife_dataframe, biopython_tree_to_alife_dataframe, alife_dataframe_to_dendropy_tree

import pandas as pd

from aux_tree_tools import tree_difference, InternalTree, sort_by_taxa_name

import dendropy as dp
import os

import pytest

assets_path = os.path.join(os.path.dirname(__file__), "assets")

def zero_out_branches(root):
    for node in root.clades:
        node.branch_length = max(node.branch_length, 0)
        zero_out_branches(node)


def test_simple_tree():
    orig_tree = dp.Tree.get(
        path=f"{assets_path}/grandtriplets_and_auntuncle.newick", schema="newick"
    )
    # orig_tree = alife_dataframe_to_dendropy_tree(
    #     pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
    # )
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
    print("distance_matrix")
    print(distance_matrix)
    reconstructed_tree = tree_reconstruction.reconstruct_tree(distance_matrix)

    print("original")
    orig_tree.print_plot(
        show_internal_node_labels=True,
        node_label_compose_fn=lambda node: f"{opyt.apply_if(node, lambda x: x.edge.length)} {opyt.apply_if(node.taxon, lambda x: x.label)}"
    )

    print("reconstructed")

    zero_out_branches(reconstructed_tree.clade)

    rec = alife_dataframe_to_dendropy_tree(
        biopython_tree_to_alife_dataframe(reconstructed_tree, {'name': 'taxon_label'},),
        setup_edge_lengths=True,
    )

    rec.reseed_at(
        rec.find_node_with_taxon_label("Inner2"),
        collapse_unrooted_basal_bifurcation=False,
    )

    print(rec.seed_node.taxon, rec.seed_node.child_nodes())

    rec.collapse_unweighted_edges()

    for node in rec:
        node.edge.length *= 2
        print(node, node.edge.length)


    rec.print_plot(
        show_internal_node_labels=True,
        node_label_compose_fn=lambda node: f"{opyt.apply_if(node, lambda x: x.edge.length)} {node.taxon.label}"
    )

    # tree_a = copy.deepcopy(tree_b)
    common_namespace = dp.TaxonNamespace()
    orig_tree.migrate_taxon_namespace(common_namespace)
    rec.migrate_taxon_namespace(common_namespace)


    original_distance_matrix = orig_tree.phylogenetic_distance_matrix()
    reconstructed_distance_matrix = rec.phylogenetic_distance_matrix()

    taxa = [node.taxon for node in orig_tree.leaf_node_iter()]

    for a, b in itertools.combinations(taxa, 2):
        print(f"{a.label=}{b.label=}: {original_distance_matrix.distance(a, b)=}, {reconstructed_distance_matrix.distance(a, b)=}")
        # assert abs(original_distance_matrix.distance(a, b) - reconstructed_distance_matrix.distance(a, b)) < 2


    print(tree_difference(
        orig_tree,
        reconstructed_tree
    ))





def test_one_tree():
    orig_tree = alife_dataframe_to_dendropy_tree(
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
    )

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

    print("original")
    orig_tree.print_plot(show_internal_node_labels=True)
    print("reconstructed")

    zero_out_branches(reconstructed_tree.clade)

    rec = alife_dataframe_to_dendropy_tree(
        biopython_tree_to_alife_dataframe(reconstructed_tree, {'name': 'taxon_label'},),
        setup_edge_lengths=True,
    )

    rec.print_plot(show_internal_node_labels=True)

    print(tree_difference(
        orig_tree,
        reconstructed_tree
    ))

def test_reconstruction_quality():
    orig_tree = alife_dataframe_to_dendropy_tree(
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
    )

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

        metrics.append(tree_difference(
            orig_tree,
            reconstructed_tree
        ))

    # make sure tree distances are increasing with resolution
    assert resolutions == sorted(resolutions)
    assert metrics == sorted(metrics)

def test_reconstructed_mrca():
    orig_tree = alife_dataframe_to_dendropy_tree(
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
    )

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

    distance_matrix = tree_reconstruction.calculate_distance_matrix(extant_population)
    reconstructed_tree = tree_reconstruction.reconstruct_tree(distance_matrix)
    reconstructed_tree = InternalTree(reconstructed_tree)

    for orig_pair, rec_pair in zip(
        itertools.combinations(orig_tree.leaf_node_iter(), 2),
        itertools.combinations(reconstructed_tree.leaf_node_iter(), 2)
    ):
        original_mrca = orig_tree.mrca(orig_pair)
        lower_mrca_bound, upper_mrca_bound = hstrat.calc_rank_of_mrca_bounds_between(*rec_pair)

        assert lower_mrca_bound < original_mrca
        assert original_mrca < upper_mrca_bound
