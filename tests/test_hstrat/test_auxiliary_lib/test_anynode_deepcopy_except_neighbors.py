import random

import anytree
import pytest

from hstrat._auxiliary_lib import anynode_deepcopy_except_neighbors


@pytest.fixture
def singleton_tree():
    root = anytree.Node("A")
    return root


@pytest.fixture
def linked_list_tree():
    root = anytree.Node("A")
    b = anytree.Node("B", parent=root)
    c = anytree.Node("C", parent=b)
    anytree.Node("D", parent=c)
    return root


@pytest.fixture
def multifurcating_tree():
    root = anytree.Node("A")
    b = anytree.Node("B", parent=root)
    c = anytree.Node("C", parent=root)
    d = anytree.Node("D", parent=root)
    anytree.Node("E", parent=b)
    anytree.Node("F", parent=c)
    anytree.Node("G", parent=c)
    anytree.Node("H", parent=d)
    anytree.Node("I", parent=d)
    anytree.Node("J", parent=d)
    return root


@pytest.fixture
def large_tree():
    max_depth = 12

    def create_tree(root, depth):
        if depth >= max_depth:
            return
        for i in range(random.choice((1, 1, 1, 1, 1, 1, 1, 2))):
            child = anytree.Node(f"{i}", parent=root)
            create_tree(child, depth + 1)

    # create the root node
    root = anytree.Node("root")
    # create tree from root
    create_tree(root, 0)
    return root


@pytest.mark.parametrize(
    "tree_fixture",
    [
        "singleton_tree",
        "linked_list_tree",
        "multifurcating_tree",
        "large_tree",
    ],
)
def test_deepcopy_except_neighbors(tree_fixture, request):
    tree = request.getfixturevalue(tree_fixture)

    snapshot_before = str(anytree.RenderTree(tree))
    for node in anytree.PreOrderIter(tree):
        children_before = node.children
        parent_before = node.parent

        node_copy = anynode_deepcopy_except_neighbors(node)
        assert node_copy.is_leaf
        assert node_copy.is_root

        assert node.children == children_before
        assert node.parent == parent_before

    snapshot_after = str(anytree.RenderTree(tree))
    assert snapshot_after == snapshot_before
