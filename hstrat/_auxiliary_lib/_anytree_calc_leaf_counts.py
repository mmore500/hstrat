import typing

import anytree

from ._AnyTreeFastPostOrderIter import AnyTreeFastPostOrderIter


def anytree_calc_leaf_counts(tree: anytree.Node) -> typing.Dict[int, int]:
    """Prepare a dict that maps each node id in a tree to the leaf count of its
    subtree.

    Parameters
    ----------
    node : anytree.Node
        The root node of the Anytree tree to compute the size of.
    """

    res = dict()
    for node in AnyTreeFastPostOrderIter(tree):
        if node.is_leaf:
            res[id(node)] = 1
        else:
            res[id(node)] = sum(res[id(child)] for child in node.children)
    return res
