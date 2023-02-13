import dendropy as dp


def sort_by_taxa_name(tree: dp.Tree) -> None:
    are_all_taxa_ints = all(isinstance(x, int) for x in tree.leaf_node_iter())

    def key_func(node):
        if are_all_taxa_ints:
            # cast label to int
            return int(node.taxon.label)
        return node.taxon.label if node.taxon is not None else ""

    for node in tree.postorder_internal_node_iter():
        # find minimum child
        min_child = min(node._child_nodes, key=key_func)

        if node.taxon is None:
            # create taxon if there is none
            node.taxon = dendropy.Taxon()

        # label internal nodes with minimum child
        node.taxon.label = min_child.taxon.label

    # sort all nodes
    for node in tree.preorder_node_iter():
        node._child_nodes.sort(key=key_func)
