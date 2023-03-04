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


def test_origin_time(inner_node):
    inner_node.origin_time = 42
    leaf_node = impl.TrieLeafNode(inner_node, "taxon")
    assert leaf_node.origin_time == 42


def test_parent(inner_node):
    leaf_node = impl.TrieLeafNode(inner_node, "taxon")
    assert leaf_node.parent is inner_node
