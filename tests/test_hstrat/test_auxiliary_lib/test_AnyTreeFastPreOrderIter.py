import random

import anytree
import contexttimer as ctt
import pytest

from hstrat._auxiliary_lib import AnyTreeFastPreOrderIter, consume


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
    all(
        n1 is n2
        for n1, n2 in zip(
            AnyTreeFastPreOrderIter(tree),
            anytree.PreOrderIter(tree),
        )
    )


def test_benchmark(large_tree):
    with ctt.Timer(factor=1000) as t_recursive:
        for __ in range(1):
            consume(anytree.PreOrderIter(large_tree))

    with ctt.Timer(factor=1000) as t_iterative:
        for __ in range(1):
            consume(AnyTreeFastPreOrderIter(large_tree))

    print(f"t_recursive={t_recursive}")
    print(f"t_iterative={t_iterative} ")
