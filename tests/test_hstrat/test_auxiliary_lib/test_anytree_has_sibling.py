import anytree

from hstrat._auxiliary_lib import anytree_has_sibling


def test_no_sibling_lone_root():
    # Create a tree with just one node
    root = anytree.Node("root")
    # Assert that the node has no siblings
    assert not anytree_has_sibling(root)


def test_no_sibling_only_child():
    # Create a tree with just one node
    root = anytree.Node("root")
    child1 = anytree.Node("child1", parent=root)
    # Assert that the node has no siblings
    assert not anytree_has_sibling(child1)


def test_single_sibling():
    # Create a tree with two sibling nodes
    root = anytree.Node("root")
    child1 = anytree.Node("child1", parent=root)
    child2 = anytree.Node("child2", parent=root)
    # Assert that child1 has at least one sibling
    assert anytree_has_sibling(child1)
    # Assert that child2 has at least one sibling
    assert anytree_has_sibling(child2)


def test_multiple_siblings():
    # Create a tree with multiple sibling nodes
    root = anytree.Node("root")
    child1 = anytree.Node("child1", parent=root)
    anytree.Node("child2", parent=root)
    grandchild1 = anytree.Node("grandchild1", parent=child1)
    grandchild2 = anytree.Node("grandchild2", parent=child1)
    # Assert that grandchild1 has at least one sibling
    assert anytree_has_sibling(grandchild1)
    # Assert that grandchild2 has at least one sibling
    assert anytree_has_sibling(grandchild2)
    # Assert that root has no siblings
    assert not anytree_has_sibling(root)


def test_root_node():
    # Create a tree with multiple nodes
    root = anytree.Node("root")
    anytree.Node("child1", parent=root)
    anytree.Node("child2", parent=root)
    # Assert that the root node has no siblings
    assert not anytree_has_sibling(root)


def test_leaf_node():
    # Create a tree with multiple nodes
    root = anytree.Node("root")
    child1 = anytree.Node("child1", parent=root)
    anytree.Node("child2", parent=root)
    anytree.Node("grandchild1", parent=child1)
    grandchild2 = anytree.Node("grandchild2", parent=child1)
    # Assert that the leaf node grandchild2 has at least one sibling
    assert anytree_has_sibling(grandchild2)
