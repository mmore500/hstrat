import anytree

from ._AnyTreeFastPreOrderIter import AnyTreeFastPreOrderIter


def anytree_cardinality(node: anytree.Node) -> int:
    """Count the number of nodes in an anytree tree rooted at the given node.

    Parameters
    ----------
    node : anytree.Node
        The root node of the Anytree tree to compute the size of.

    Returns
    -------
    int
        The number of nodes in the tree rooted at the given node.
    """
    return sum(1 for _ in AnyTreeFastPreOrderIter(node))
