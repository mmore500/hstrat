import anytree
import pytest

from hstrat._auxiliary_lib import (
    anytree_cardinality,
    anytree_peel_sibling_to_cousin,
    is_in,
)


def test_anytree_peel_sibling_to_cousin_with_leaf_node():
    #    A
    #   / \
    #  B   C
    # /
    # D
    root = anytree.Node("A")
    b = anytree.Node("B", parent=root)
    anytree.Node("C", parent=root)
    d = anytree.Node("D", parent=b)

    with pytest.raises(AssertionError):
        anytree_peel_sibling_to_cousin(d)

    # Tree structure should not change
    #    A
    #   / \
    #  B   C
    # /
    # D


def test_anytree_peel_sibling_to_cousin_with_node_without_sibling():
    #    A
    #   / \
    #  B   C
    root = anytree.Node("A")
    anytree.Node("B", parent=root)
    anytree.Node("C", parent=root)

    with pytest.raises(AssertionError):
        anytree_peel_sibling_to_cousin(root)

    # Tree structure should not change
    #    A
    #   / \
    #  B   C


def test_anytree_peel_sibling_to_cousin_with_node_with_sibling():
    #    A
    #   / \
    #  B   C
    # / \
    # D   E
    #    / \
    #   F   G
    a = anytree.Node("A")
    b = anytree.Node("B", parent=a)
    c = anytree.Node("C", parent=a)
    d = anytree.Node("D", parent=b)
    e = anytree.Node("E", parent=b)
    f = anytree.Node("F", parent=e)
    g = anytree.Node("G", parent=e)
    assert anytree_cardinality(a) == 7

    anytree_peel_sibling_to_cousin(e)
    # Tree structure after the first peel:
    #    A
    #   /|\
    #  B C B'
    #  |   |
    #  D   E
    #     / \
    #    F   G

    b_prime = next(node for node in a.children if not is_in(node, (b, c)))
    assert b_prime.name == "B"

    assert anytree_cardinality(a) == 8
    assert a.parent is None
    assert b.parent is a
    assert b_prime.parent is a
    assert c.parent is a
    assert d.parent is b
    assert e.parent is b_prime
    assert f.parent is e
    assert g.parent is e

    anytree_peel_sibling_to_cousin(g)
    # Tree structure after the second peel:
    #    A
    #   /|\
    #  B C B'
    #  |  / \
    #  D  E  E'
    #     |  |
    #     F  G

    e_prime = next(node for node in b_prime.children if node is not e)
    assert e_prime.name == "E"

    assert anytree_cardinality(a) == 9
    assert a.parent is None
    assert b.parent is a
    assert b_prime.parent is a
    assert c.parent is a
    assert d.parent is b
    assert e.parent is b_prime
    assert e_prime.parent is b_prime
    assert f.parent is e
    assert g.parent is e_prime

    anytree_peel_sibling_to_cousin(e_prime)
    # Tree structure after the third peel:
    #      A
    #   /|\  \
    #  B C B' B''
    #  |   |  |
    #  D   E  E'
    #      |  |
    #      F  G

    b_double_prime = next(
        node for node in a.children if not is_in(node, (b, c, b_prime))
    )
    assert b_double_prime.name == "B"

    assert anytree_cardinality(a) == 10
    assert a.parent is None
    assert b.parent is a
    assert b_prime.parent is a
    assert b_double_prime.parent is a
    assert c.parent is a
    assert d.parent is b
    assert e.parent is b_prime
    assert e_prime.parent is b_double_prime
    assert f.parent is e
    assert g.parent is e_prime
