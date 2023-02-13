import dendropy as dp

from ._AuxTree import AuxTree
from ._sort_by_taxa_name import sort_by_taxa_name


def tree_distance_metric(x, y) -> float:
    # use dendropy trees
    tree_a = AuxTree(x).dendropy
    tree_b = AuxTree(y).dendropy

    # tree_a = copy.deepcopy(tree_b)
    common_namespace = dp.TaxonNamespace()
    tree_a.migrate_taxon_namespace(common_namespace)
    tree_b.migrate_taxon_namespace(common_namespace)

    tree_a.encode_bipartitions()
    for bp in tree_a.bipartition_encoding:
        bp.is_mutable = False
    tree_b.encode_bipartitions()
    for bp in tree_b.bipartition_encoding:
        bp.is_mutable = False

    # sort_by_taxa_name(tree_a)
    # sort_by_taxa_name(tree_b)

    # tree_b.reseed_at(
    #     tree_b.find_node_with_taxon_label("Inner2"),
    #     collapse_unrooted_basal_bifurcation=False,
    # )
    # tree_a.print_plot(
    #     show_internal_node_labels=True,
    #     plot_metric='level'
    # )
    # tree_b.print_plot(
    #     show_internal_node_labels=True,
    #     plot_metric='level'
    # )

    # tree_a.collapse_unweighted_edges()
    # tree_b.collapse_unweighted_edges()

    # tree_a.print_plot(
    #     show_internal_node_labels=True,
    #     plot_metric='level'
    # )
    # tree_b.print_plot(
    #     show_internal_node_labels=True,
    #     plot_metric='level'
    # )
    # print("tree_a, tree_b", dp.calculate.treecompare.false_positives_and_negatives(tree_a, tree_b))
    # print("tree_b, tree_a", dp.calculate.treecompare.false_positives_and_negatives(tree_b, tree_a))

    # print("tree_a", len(set(tree_a.bipartition_encoding)))
    # print("tree_b", len(set(tree_b.bipartition_encoding)))

    # print(sorted([x.level() for x in tree_a]))
    # print(sorted([x.level() for x in tree_b]))

    return dp.calculate.treecompare.symmetric_difference(
        tree_a, tree_b, is_bipartitions_updated=True
    )
