import anytree

from hstrat._auxiliary_lib import anytree_cardinality


def test_empty_tree():
    # Create an empty tree
    root = anytree.Node("root")
    # Assert that the length of the tree is 1 (just the root node)
    assert anytree_cardinality(root) == 1


def test_single_node_tree():
    # Create a tree with just one node
    root = anytree.Node("root")
    # Assert that the length of the tree is 1
    assert anytree_cardinality(root) == 1


def test_two_node_tree():
    # Create a tree with two nodes
    root = anytree.Node("root")
    anytree.Node("child1", parent=root)
    # Assert that the length of the tree is 2 (root and child1)
    assert anytree_cardinality(root) == 2


def test_multi_level_tree():
    # Create a multi-level tree
    root = anytree.Node("root")
    child1 = anytree.Node("child1", parent=root)
    child2 = anytree.Node("child2", parent=root)
    anytree.Node("grandchild1", parent=child1)
    anytree.Node("grandchild2", parent=child1)
    anytree.Node("grandchild3", parent=child2)
    # Assert that the length of the tree is 6 (root, child1, child2, grandchild1, grandchild2, and grandchild3)
    assert anytree_cardinality(root) == 6
