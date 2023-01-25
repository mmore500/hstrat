from alifedata_phyloinformatics_convert import biopython_tree_to_alife_dataframe, alife_dataframe_to_dendropy_tree, dendropy_tree_to_alife_dataframe, alife_dataframe_to_biopython_tree
import dendropy
from dendropy.calculate.treecompare import symmetric_difference
import pandas as pd
import Bio
from dendropy.calculate.treecompare import false_positives_and_negatives

# auxiliary tree class to allow for inter-format conversions
class AuxTree():
    def __init__(self, tree):
        # internal tree representation is an alife-formatted tree
        self._tree = self._alife_dispatcher(tree)

    @property
    def biopython(self):
        return alife_dataframe_to_biopython_tree(self._tree)

    @property
    def dendropy(self):
        return alife_dataframe_to_dendropy_tree(self._tree)

    @property
    def alife(self):
        return self._tree

    def _alife_dispatcher(self, tree):
        """
        Convert any supported tree format to ALife format
        """
        if isinstance(tree, dendropy.Tree):
            # is a Dendropy Tree
            return dendropy_tree_to_alife_dataframe(tree) #, {'name': 'taxon_label'})
        if isinstance(tree, pd.DataFrame):
            # is an Alife Dataframe
            # TODO: check these properties exist https://alife-data-standards.github.io/alife-data-standards/phylogeny.html
            return tree
        if isinstance(tree, Bio.Phylo.BaseTree.Tree):
            # is a biopython tree
            return biopython_tree_to_alife_dataframe(tree, {'name': 'taxon_label'})

def sort_by_taxa_name(tree):
    are_all_taxa_ints = all(
        isinstance(x, int) for x in tree.leaf_node_iter()
    )

    def key_func(node):
        if are_all_taxa_ints:
            # cast label to int
            return int(node.taxon.label)
        return node.taxon.label if node.taxon is not None else ""

    for node in tree.postorder_internal_node_iter():
        # find minimum child
        min_child = min(
            node._child_nodes,
            key=key_func
        )

        if node.taxon is None:
            # create taxon if there is none
            node.taxon = dendropy.Taxon()

        # label internal nodes with minimum child
        node.taxon.label = min_child.taxon.label

    # sort all nodes
    for node in tree.preorder_node_iter():
        node._child_nodes.sort(key=key_func)

def tree_difference(x, y):
    # use dendropy trees
    tree_a = AuxTree(x).dendropy
    tree_b = AuxTree(y).dendropy

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
