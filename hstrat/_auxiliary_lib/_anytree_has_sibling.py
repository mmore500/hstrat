import anytree


def anytree_has_sibling(node: anytree.node) -> bool:
    """Check whether the given node has at least one sibling in the Anytree
    tree.

    Parameters
    ----------
    node : anytree.node
        The node to check for siblings.

    Returns
    -------
    bool
        True if the node has at least one sibling in the tree, False otherwise.
    """
    return node.parent is not None and len(node.parent.children) > 1
