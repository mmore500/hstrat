import typing

import anytree


class AnyTreeFastPreOrderIter:
    r"""Iterator that traverses an `anytree.AnyNode` tree using pre-order
    strategy (self, children).

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

    We can create an instance of `AnyTreeFastPreOrderIter` and use it to
    iterate over the tree:

    >>> from anytree import Node
    >>> root = Node("a")
    >>> b = Node("b", parent=root)
    >>> c = Node("c", parent=root)
    >>> d = Node("d", parent=b)
    >>> e = Node("e", parent=b)
    >>> f = Node("f", parent=c)
    >>> for node in AnyTreeFastPreOrderIter(root):
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
    This implementationis faster than the `PreOrderIter` implementation provided by `anytree` (especially for large trees). Because it is iterative instead of recursive, it will won't cause recursion limit errors.
    """

    _stack: typing.List[anytree.AnyNode]

    def __init__(
        self: "AnyTreeFastPreOrderIter", root: anytree.AnyNode
    ) -> None:
        """Initialize the iterator.

        Parameters
        ----------
        root : anytree.AnyNode
            The root node of the tree to iterate over.
        """
        self._stack = [root]

    def __iter__(self: "AnyTreeFastPreOrderIter") -> "AnyTreeFastPreOrderIter":
        """Return the iterator object itself.

        Returns
        -------
        AnyTreeFastPreOrderIter
            The iterator object itself.
        """
        return self

    def __next__(self: "AnyTreeFastPreOrderIter") -> anytree.AnyNode:
        """Return the next node in pre-order traversal.

        Returns
        -------
        anytree.AnyNode
            The next node in pre-order traversal.

        Raises
        ------
        StopIteration
            When there are no more nodes to traverse.
        """
        if not self._stack:
            raise StopIteration

        node = self._stack.pop()

        if node.children:
            self._stack.extend(reversed(node.children))

        return node
