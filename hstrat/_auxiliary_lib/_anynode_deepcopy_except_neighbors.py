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
    hasattr_parent = hasattr(node, "_NodeMixin__parent")

    # temporarily detach parent and children
    detached_children, node._NodeMixin__children = (
        node._NodeMixin__children,
        list(),
    )
    if hasattr_parent:
        detached_parent, node._NodeMixin__parent = (
            node._NodeMixin__parent,
            None,
        )

    res = copy.deepcopy(node)

    # reattach parent and children
    node._NodeMixin__children = detached_children
    if hasattr_parent:
        node._NodeMixin__parent = detached_parent

    return res
