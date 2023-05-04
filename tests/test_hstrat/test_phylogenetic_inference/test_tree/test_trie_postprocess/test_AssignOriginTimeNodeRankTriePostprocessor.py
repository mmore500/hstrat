import anytree

from hstrat import hstrat
import hstrat.phylogenetic_inference.tree._impl as impl


def test_assign_trie_origin_times_node_rank_single_leaf():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    leaf = impl.TrieLeafNode(parent=inner, taxon_label="A")
    root = hstrat.AssignOriginTimeNodeRankTriePostprocessor()(
        root, p_differentia_collision=0.5, mutate=True
    )
    assert leaf.origin_time == 0
    assert inner.origin_time == 0
    assert root.origin_time == 0


def test_assign_trie_origin_times_node_rank_two_leaves():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    leaf1 = impl.TrieLeafNode(parent=inner, taxon_label="A")
    leaf2 = impl.TrieLeafNode(parent=inner, taxon_label="B")
    root = hstrat.AssignOriginTimeNodeRankTriePostprocessor()(
        root, p_differentia_collision=0.5, mutate=True
    )
    assert root.origin_time == 0
    assert inner.origin_time == 0
    assert leaf1.origin_time == 0
    assert leaf2.origin_time == 0


def test_assign_trie_origin_times_node_rank1():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner1 = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    inner2 = impl.TrieInnerNode(rank=1, differentia=10, parent=inner1)
    leaf = impl.TrieLeafNode(parent=inner2, taxon_label="A")
    root = hstrat.AssignOriginTimeNodeRankTriePostprocessor()(
        root, p_differentia_collision=0.5, mutate=True
    )
    assert root.origin_time == 0
    assert inner1.origin_time == 0
    assert inner2.origin_time == 1
    assert leaf.origin_time == 1


def test_assign_trie_origin_times_node_rank2():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner1 = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    inner2 = impl.TrieInnerNode(rank=2, differentia=10, parent=inner1)
    leaf = impl.TrieLeafNode(parent=inner2, taxon_label="A")
    root = hstrat.AssignOriginTimeNodeRankTriePostprocessor()(
        root, p_differentia_collision=0.5, mutate=True
    )
    assert root.origin_time == 0
    assert inner1.origin_time == 0
    assert inner2.origin_time == 2
    assert leaf.origin_time == 2


def test_assign_trie_origin_times_node_rank3():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner1 = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    inner2 = impl.TrieInnerNode(rank=3, differentia=10, parent=inner1)
    leaf = impl.TrieLeafNode(parent=inner2, taxon_label="A")
    root = hstrat.AssignOriginTimeNodeRankTriePostprocessor()(
        root, p_differentia_collision=0.5, mutate=True
    )
    assert root.origin_time == 0
    assert inner1.origin_time == 0
    assert inner2.origin_time == 3
    assert leaf.origin_time == 3


def test_assign_trie_origin_times_node_rank_complex():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner1 = impl.TrieInnerNode(rank=0, differentia=0, parent=root)

    inner2 = impl.TrieInnerNode(rank=4, differentia=10, parent=inner1)
    inner3 = impl.TrieInnerNode(rank=7, differentia=7, parent=inner2)

    inner2a = impl.TrieInnerNode(rank=1, differentia=1, parent=inner1)

    leaf3_a = impl.TrieLeafNode(parent=inner3, taxon_label="leaf3a_a")

    leaf2a_a = impl.TrieLeafNode(parent=inner2a, taxon_label="leaf2a_a")
    leaf2a_b = impl.TrieLeafNode(parent=inner2a, taxon_label="leaf2a_b")

    root = hstrat.AssignOriginTimeNodeRankTriePostprocessor()(
        root, p_differentia_collision=0.5, mutate=True
    )

    assert root.origin_time == 0
    assert inner1.origin_time == 0
    assert inner2.origin_time == 4
    assert inner3.origin_time == 7
    assert inner2a.origin_time == 1
    assert leaf2a_a.origin_time == 1
    assert leaf2a_b.origin_time == 1
    assert leaf3_a.origin_time == 7


def test_assign_trie_origin_times_node_rank_assigned_property():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    leaf = impl.TrieLeafNode(parent=inner, taxon_label="A")
    root = hstrat.AssignOriginTimeNodeRankTriePostprocessor(
        assigned_property="blueberry"
    )(root, p_differentia_collision=0.5, mutate=True)
    assert leaf.blueberry == 0
    assert inner.blueberry == 0
    assert root.blueberry == 0


def test_assign_trie_origin_times_node_rank_mutate():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    leaf = impl.TrieLeafNode(parent=inner, taxon_label="A")
    root_ = hstrat.AssignOriginTimeNodeRankTriePostprocessor(
        assigned_property="blueberry"
    )(root, p_differentia_collision=0.5, mutate=False)
    assert not hasattr(leaf, "blueberry")
    assert not hasattr(inner, "blueberry")
    assert not hasattr(root, "blueberry")

    assert hasattr(root_, "blueberry")

    root = hstrat.AssignOriginTimeNodeRankTriePostprocessor(
        assigned_property="blueberry",
    )(root, p_differentia_collision=0.5, mutate=True)
    assert str(anytree.RenderTree(root).by_attr("blueberry")) == str(
        anytree.RenderTree(root_).by_attr("blueberry")
    )
