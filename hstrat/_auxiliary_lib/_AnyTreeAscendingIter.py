import typing

import anytree


def AnyTreeAscendingIter(
    node: anytree.AnyNode,
) -> typing.Iterator[anytree.AnyNode]:
    """Iterate over the ancestors of a given node in ascending order.

    Parameters
    ----------
    node : anytree.AnyNode
        A node in an anytree tree.

    Yields
    ------
    anytree.AnyNode
        The sequence of anytree.AnyNode objects representing the lineage of
        the given node in ascending order, starting from the node itself.

    Examples
    --------
    >>> root = anytree.Node("A")
    >>> b = anytree.Node("B", parent=root)
    >>> c = anytree.Node("C", parent=b)
    >>> d = anytree.Node("D", parent=b)
    >>> e = anytree.Node("E", parent=c)
    >>> f = anytree.Node("F", parent=d)
    >>> g = anytree.Node("G", parent=d)
    >>> list(AnyTreeAscendingIter(e))
    [Node('/A/B/C/E'), Node('/A/B/C'), Node('/A/B'), Node('/A')]
    """
    while node is not None:
        yield node
        node = node.parent
