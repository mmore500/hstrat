from alifedata_phyloinformatics_convert import biopython_tree_to_alife_dataframe, alife_dataframe_to_dendropy_tree
import dendropy
from dendropy.calculate.treecompare import symmetric_difference
import pandas as pd
import Bio
from dendropy.calculate.treecompare import false_positives_and_negatives

class MetaTree(type):
    @staticmethod
    def __call__(tree):
        if isinstance(tree, dendropy.Tree):
            # no conversion needed
            return tree
        if isinstance(tree, pd.DataFrame):
            # is an Alife Dataframe
            return alife_dataframe_to_dendropy_tree(tree, setup_edge_lengths=True)
        if isinstance(tree, Bio.Phylo.BaseTree.Tree):
            # is a biopython tree
            return InternalTree(biopython_tree_to_alife_dataframe(tree, {'name': 'taxon_label'}))

class InternalTree(metaclass=MetaTree):
    pass

def sort_by_taxa_name(tree):
    for node in tree.postorder_internal_node_iter():
        # find minimum child
        min_child = min(
            node._child_nodes,
            key=lambda x: x.taxon.label if x.taxon is not None else ""
        )

        # label internal nodes with minimum child
        if node.taxon is not None:
            node.taxon.label = min_child.taxon.label
        else:
            node.taxon = dendropy.Taxon(label=min_child.taxon.label)

    for node in tree.preorder_node_iter():
        node._child_nodes.sort(key=lambda node: node.taxon.label)

def tree_difference(x, y):
    tree_a = InternalTree(x)
    tree_b = InternalTree(y)

    # tree_a = copy.deepcopy(tree_b)
    common_namespace = dendropy.TaxonNamespace()
    tree_a.migrate_taxon_namespace(common_namespace)
    tree_b.migrate_taxon_namespace(common_namespace)

    tree_a.encode_bipartitions()
    for bp in tree_a.bipartition_encoding:
        bp.is_mutable = False
    tree_b.encode_bipartitions()
    for bp in tree_b.bipartition_encoding:
        bp.is_mutable = False


    # # print("tree_a")
    # sort_by_taxa_name(tree_a)
    # # print("tree_b")
    # sort_by_taxa_name(tree_b)


    # tree_b.reseed_at(
    #     tree_b.find_node_with_taxon_label("Inner2"),
    #     collapse_unrooted_basal_bifurcation=False,
    # )

    tree_a.collapse_unweighted_edges()
    tree_b.collapse_unweighted_edges()


    tree_a.print_plot(
        show_internal_node_labels=True,
        plot_metric='level'
    )
    tree_b.print_plot(
        show_internal_node_labels=True,
        plot_metric='level'
    )

    print("tree_a, tree_b", false_positives_and_negatives(tree_a, tree_b))
    print("tree_b, tree_a", false_positives_and_negatives(tree_b, tree_a))

    print("tree_a", len(set(tree_a.bipartition_encoding)))
    print("tree_b", len(set(tree_b.bipartition_encoding)))


    print(sorted([x.level() for x in tree_a]))
    print(sorted([x.level() for x in tree_b]))



    return symmetric_difference(
        tree_a,
        tree_b,
        is_bipartitions_updated=False
    )
