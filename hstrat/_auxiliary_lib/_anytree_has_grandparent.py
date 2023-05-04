import anytree


def anytree_has_grandparent(node: anytree.node) -> bool:
    """Check whether the given node is located at or below level two of its
    tree.

    Parameters
    ----------
    node : anytree.node
        The node to check.

    Returns
    -------
    bool
        True if the node has a grandparent in the tree, False otherwise.
    """
    return node.parent is not None and node.parent.parent is not None
