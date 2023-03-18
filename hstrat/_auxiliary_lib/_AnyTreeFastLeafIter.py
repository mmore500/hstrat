import typing

import anytree

from ._AnyTreeFastPreOrderIter import AnyTreeFastPreOrderIter


def AnyTreeFastLeafIter(
    node: anytree.AnyNode,
) -> typing.Iterator[anytree.AnyNode]:
    """Efficiently iterate over the leaf nodes of an AnyTree structure

    Parameters
    ----------
    node : anytree.AnyNode
        The root node of the tree (or subtree) for which the leaf nodes are to
        be iterated.

    Returns
    -------
    typing.Iterator[anytree.AnyNode]
        An iterator over leaf nodes of the tree (or subtree) rooted at `node`.
    """
    yield from filter(lambda x: x.is_leaf, AnyTreeFastPreOrderIter(node))
