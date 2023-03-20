import anytree
import pytest

from hstrat._auxiliary_lib import anytree_has_grandparent


@pytest.fixture
def tree():
    root = anytree.Node("A")
    b = anytree.Node("B", parent=root)
    c = anytree.Node("C", parent=b)
    anytree.Node("D", parent=c)
    e = anytree.Node("E", parent=root)
    anytree.Node("F", parent=e)
    anytree.Node("X", parent=root)
    return root


def test_node_has_grandparent(tree):
    assert anytree_has_grandparent(tree.children[0].children[0])
    assert anytree_has_grandparent(tree.children[1].children[0])


def test_root_node_has_no_grandparent(tree):
    assert not anytree_has_grandparent(tree)
    assert not anytree_has_grandparent(anytree.Node("root"))


def test_node_has_no_grandparent(tree):
    for child in tree.children:
        assert not anytree_has_grandparent(child)
