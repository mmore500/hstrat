from collections import deque
import typing

import anytree


class AnyTreeFastLevelOrderIter:
    r"""Iterator that traverses an `anytree.AnyNode` tree using level-order
    strategy.

    Parameters
    ----------
    root : anytree.AnyNode
        The root node of the tree to iterate over.

    Examples
    --------
    Given the following tree:

        a
       / \
      b   c
     / \   \
    d   e   f

    We can create an instance of `AnyTreeFastLevelOrderIter` and use it to
    iterate over the tree:

    >>> from anytree import Node
    >>> root = Node("a")
    >>> b = Node("b", parent=root)
    >>> c = Node("c", parent=root)
    >>> d = Node("d", parent=b)
    >>> e = Node("e", parent=b)
    >>> f = Node("f", parent=c)
    >>> for node in AnyTreeFastLevelOrderIter(root):
    ...     print(node.name)
    ...
    a
    b
    c
    d
    e
    f

    Notes
    -----
    This implementation is faster than the `LevelOrderIter` implementation
    provided by `anytree` (especially for large trees). Because it is iterative
    instead of recursive, it won't cause recursion limit errors.
    """

    _queue: typing.Deque[anytree.AnyNode]

    def __init__(
        self: "AnyTreeFastLevelOrderIter", root: anytree.AnyNode
    ) -> None:
        """Initialize the iterator.

        Parameters
        ----------
        root : anytree.AnyNode
            The root node of the tree to iterate over.
        """
        self._queue = deque([root])

    def __iter__(
        self: "AnyTreeFastLevelOrderIter",
    ) -> "AnyTreeFastLevelOrderIter":
        """Return the iterator object itself.

        Returns
        -------
        AnyTreeFastLevelOrderIter
            The iterator object itself.
        """
        return self

    def __next__(self: "AnyTreeFastLevelOrderIter") -> anytree.AnyNode:
        """Return the next node in level-order traversal.

        Returns
        -------
        anytree.AnyNode
            The next node in level-order traversal.

        Raises
        ------
        StopIteration
            When there are no more nodes to traverse.
        """
        if not self._queue:
            raise StopIteration

        node = self._queue.popleft()
        self._queue.extend(node.children)

        return node
