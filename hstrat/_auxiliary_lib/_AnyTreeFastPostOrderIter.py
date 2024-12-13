from collections import deque
import typing

import anytree


class AnyTreeFastPostOrderIter:
    r"""Iterator that traverses an `anytree.AnyNode` tree using post-order
    strategy (children, self).

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

    We can create an instance of `AnyTreeFastPostOrderIter` and use it to
    iterate over the tree:

    >>> from anytree import Node
    >>> root = Node("a")
    >>> b = Node("b", parent=root)
    >>> c = Node("c", parent=root)
    >>> d = Node("d", parent=b)
    >>> e = Node("e", parent=b)
    >>> f = Node("f", parent=c)
    >>> for node in AnyTreeFastPostOrderIter(root):
    ...     print(node.name)
    ...
    d
    e
    b
    f
    c
    a

    Notes
    -----
    This implementation is faster than the `LevelOrderIter` implementation
    provided by `anytree` (especially for large trees). Because it is iterative
    instead of recursive, it won't cause recursion limit errors.
    """

    _stack: typing.Deque[anytree.AnyNode]
    _visited: typing.Set[anytree.AnyNode]
    _current: anytree.AnyNode
    _next_node: typing.Optional[anytree.AnyNode]

    def __init__(
        self: "AnyTreeFastPostOrderIter", root: anytree.AnyNode
    ) -> None:
        """Initialize the iterator.

        Parameters
        ----------
        root : anytree.AnyNode
            The root node of the tree to iterate over.
        """
        self._stack = deque()
        self._visited = set()
        self._current = root
        self._next_node = None
        self._traverse_leftmost_path()

    def _traverse_leftmost_path(self: "AnyTreeFastPostOrderIter"):
        """Traverse the leftmost path of the current node, adding visited nodes
        to the stack and setting `_next_node` to the current node when we reach
        the end of the path.

        Also updates the `_visited` set to avoid revisiting nodes.
        """
        while self._current is not None:
            self._stack.append(self._current)
            for child in self._current.children:
                if child not in self._visited:
                    self._current = child
                    break
            else:
                self._next_node = self._current
                self._visited.add(self._current)
                self._current = None

    def __iter__(
        self: "AnyTreeFastPostOrderIter",
    ) -> "AnyTreeFastPostOrderIter":
        """Return the iterator object itself.

        Returns
        -------
        AnyTreeFastPostOrderIter
            The iterator object itself.
        """
        return self

    def __next__(self: "AnyTreeFastPostOrderIter") -> anytree.AnyNode:
        """Return the next node in post-order traversal.

        Returns
        -------
        anytree.AnyNode
            The next node in post-order traversal.

        Raises
        ------
        StopIteration
            When there are no more nodes to traverse.
        """
        if self._next_node is None:
            raise StopIteration
        node = self._next_node
        self._next_node = None
        if len(self._stack) == 0:
            return node
        parent = self._stack.pop()
        if parent.parent is not None and parent.parent not in self._visited:
            self._current = parent.parent
            self._traverse_leftmost_path()
        return node
