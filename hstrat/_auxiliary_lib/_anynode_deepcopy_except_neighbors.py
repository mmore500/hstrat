import copy

import anytree


def anynode_deepcopy_except_neighbors(
    node: anytree.AnyNode,
) -> anytree.AnyNode:
    """Create a deep copy of an AnyNode object, excluding its parents and
    children.

    Parameters
    ----------
    node : anytree.AnyNode
        The AnyNode object to be copied.

    Returns
    -------
    anytree.AnyNode
        A new AnyNode object with the same attributes and values as the
        original, but with no parent or children.
    """
    # temporarily detach parent and children
    detached_children, node.children = (
        node.children,
        tuple(),
    )
    detached_parent, node.parent = (
        node.parent,
        None,
    )

    res = copy.deepcopy(node)

    # reattach parent and children
    node.children = detached_children
    node.parent = detached_parent

    return res
