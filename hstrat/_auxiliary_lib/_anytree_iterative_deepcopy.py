from collections import deque
import typing

import anytree

from ._AnyTreeFastLevelOrderIter import AnyTreeFastLevelOrderIter
from ._anynode_deepcopy_except_neighbors import (
    anynode_deepcopy_except_neighbors,
)


def anytree_iterative_deepcopy(
    node: anytree.AnyNode,
    progress_wrap: typing.Callable = lambda x: x,
) -> anytree.AnyNode:
    """Create a deep copy of an anytree tree without recursing over the tree
    structure.

    Parameters
    ----------
    node : anytree.AnyNode
        The root node of the anytree tree or subtree to copy.

    Returns
    -------
    anytree.AnyNode
        A new tree with the same structure and attributes as the original tree,
        but with no shared objects.
    """
    parent_from_deque = deque([node.parent])
    parent_to_deque = deque([None])

    for node_from in progress_wrap(AnyTreeFastLevelOrderIter(node)):

        while node_from.parent is not parent_from_deque[-1]:
            parent_from_deque.pop()
            parent_to_deque.pop()

        assert parent_from_deque[-1] is node_from.parent

        node_to = anynode_deepcopy_except_neighbors(node_from)
        # assigning to parent casues expensive __check_loop safety check
        # use internal __attach method instead
        node_to._NodeMixin__attach(parent_to_deque[-1])

        parent_from_deque.appendleft(node_from)
        parent_to_deque.appendleft(node_to)

    return node_to.root  # anytree uses a non-recursive implemenation
