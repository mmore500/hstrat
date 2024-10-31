import anytree
import pytest

import hstrat.phylogenetic_inference.tree._impl as impl


@pytest.fixture
def inner_node():
    return anytree.AnyNode()


def test_taxon_label(inner_node):
    leaf_node = impl.TrieLeafNode(inner_node, "taxon")
    assert leaf_node.taxon_label == "taxon"


def test_taxon(inner_node):
    leaf_node = impl.TrieLeafNode(inner_node, "taxon")
    assert leaf_node.taxon == "taxon"


def test_parent(inner_node):
    leaf_node = impl.TrieLeafNode(inner_node, "taxon")
    assert leaf_node.parent is inner_node


def test_eq(inner_node):
    leaf_node = impl.TrieLeafNode(inner_node, "taxon")
    other_node = impl.TrieLeafNode(inner_node, "taxon")
    not_eq_node = impl.TrieLeafNode(inner_node, "other_taxon")
    assert leaf_node == other_node
    assert not_eq_node != leaf_node
