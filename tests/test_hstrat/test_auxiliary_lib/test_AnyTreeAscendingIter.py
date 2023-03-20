import random

import anytree
import pytest

from hstrat._auxiliary_lib import AnyTreeAscendingIter


@pytest.fixture
def singleton_tree():
    root = anytree.Node("A")
    return root


@pytest.fixture
def linked_list_tree():
    root = anytree.Node("A")
    b = anytree.Node("B", parent=root)
    c = anytree.Node("C", parent=b)
    _ = d = anytree.Node("D", parent=c)
    return root


@pytest.fixture
def multifurcating_tree():
    root = anytree.Node("A")
    b = anytree.Node("B", parent=root)
    c = anytree.Node("C", parent=root)
    d = anytree.Node("D", parent=root)
    _ = e = anytree.Node("E", parent=b)
    _ = f = anytree.Node("F", parent=c)
    _ = g = anytree.Node("G", parent=c)
    _ = h = anytree.Node("H", parent=d)
    _ = i = anytree.Node("I", parent=d)
    _ = j = anytree.Node("J", parent=d)
    return root


@pytest.fixture
def large_tree():
    max_depth = 50

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
def test_preorder_iterator(tree_fixture, request):
    tree = request.getfixturevalue(tree_fixture)
    for node in anytree.PreOrderIter(tree):
        assert all(
            n1 is n2
            for n1, n2 in zip(
                AnyTreeAscendingIter(node),
                node.iter_path_reverse(),
            )
        )
