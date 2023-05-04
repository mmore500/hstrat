import anytree

from ._anytree_has_sibling import anytree_has_sibling
from ._anytree_iterative_deepcopy import anytree_iterative_deepcopy


def anytree_peel_sibling_to_cousin(node: anytree.Node) -> None:
    """Peels a node from its sibling group and moves it to a new cousin
    position in the tree.

    Parameters
    ----------
    node : anytree.Node
        The node to be peeled.

    Raises
    ------
    AssertionError
        If the node is a leaf node or has no sibling or no grandparent.

    Notes
    -----
    This function clones the parent node of the input node and attaches it to
    the input node's grandparent node. The input node is then grafted away from
    its original parent and onto the newly cloned parent node as a child. The
    original parent node is left in place with any remaining children.

    Examples
    --------
    Create a tree with 3 levels of nodes, and peel a sibling node:

    >>> import anytree
    >>> from hstrat._auxiliary_lib import anytree_peel_sibling_to_cousin
    >>> a = anytree.Node("A")
    >>> b = anytree.Node("B", parent=a)
    >>> c = anytree.Node("C", parent=a)
    >>> d = anytree.Node("D", parent=b)
    >>> e = anytree.Node("E", parent=b)
    >>> f = anytree.Node("F", parent=e)
    >>> g = anytree.Node("G", parent=e)
    >>> print(anytree.RenderTree(a))
    Node('/A')
    ├── Node('/A/B')
    │   ├── Node('/A/B/D')
    │   └── Node('/A/B/E')
    │       ├── Node('/A/B/E/F')
    │       └── Node('/A/B/E/G')
    └── Node('/A/C')
    >>> anytree_peel_sibling_to_cousin(e)
    >>> print(anytree.RenderTree(a))
    Node('/A')
    ├── Node('/A/C')
    ├── Node('/A/B')
    │   └── Node('/A/B/D')
    └── Node('/A/B')
        └── Node('/A/B/E')
            ├── Node('/A/B/E/F')
            └── Node('/A/B/E/G')
    """
    assert node.parent is not None
    assert node.parent.parent is not None
    assert anytree_has_sibling(node)

    parent = node.parent

    peeled_parent = anytree_iterative_deepcopy(parent)
    peeled_parent.parent = parent.parent

    parent.children = filter(lambda x: x is not node, parent.children)

    assert node.parent is None
    peeled_parent.children = [node]
