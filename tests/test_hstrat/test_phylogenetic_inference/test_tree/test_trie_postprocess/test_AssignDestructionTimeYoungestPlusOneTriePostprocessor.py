import math

import anytree

from hstrat import hstrat
import hstrat.phylogenetic_inference.tree._impl as impl
import hstrat.phylogenetic_inference.tree.trie_postprocess._detail as detail


def test_base_class():
    assert issubclass(
        hstrat.AssignDestructionTimeYoungestPlusOneTriePostprocessor,
        detail.TriePostprocessorBase,
    )


def test_assign_trie_destruction_time_youngestplus1_single_leaf():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    leaf = impl.TrieLeafNode(parent=inner, taxon_label="A")
    root = hstrat.CompoundTriePostprocessor(
        [
            hstrat.AssignOriginTimeNaiveTriePostprocessor(),
            hstrat.AssignDestructionTimeYoungestPlusOneTriePostprocessor(),
        ],
    )(root, p_differentia_collision=0.5, mutate=True)
    assert leaf.destruction_time == math.inf
    assert inner.destruction_time == 1
    assert root.destruction_time == 1


def test_assign_trie_destruction_time_youngestplus1_two_leaves():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    leaf1 = impl.TrieLeafNode(parent=inner, taxon_label="A")
    leaf2 = impl.TrieLeafNode(parent=inner, taxon_label="B")
    root = hstrat.CompoundTriePostprocessor(
        [
            hstrat.AssignOriginTimeNaiveTriePostprocessor(),
            hstrat.AssignDestructionTimeYoungestPlusOneTriePostprocessor(),
        ],
    )(root, p_differentia_collision=0.5, mutate=True)
    assert root.destruction_time == 1
    assert inner.destruction_time == 1
    assert leaf1.destruction_time == math.inf
    assert leaf2.destruction_time == math.inf


def test_assign_trie_destruction_time_youngestplus1_1():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner1 = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    inner2 = impl.TrieInnerNode(rank=1, differentia=10, parent=inner1)
    leaf = impl.TrieLeafNode(parent=inner2, taxon_label="A")
    root = hstrat.CompoundTriePostprocessor(
        [
            hstrat.AssignOriginTimeNaiveTriePostprocessor(),
            hstrat.AssignDestructionTimeYoungestPlusOneTriePostprocessor(),
        ],
    )(root, p_differentia_collision=0.5, mutate=True)
    assert root.destruction_time == 1
    assert inner1.destruction_time == 2
    assert inner2.destruction_time == 2
    assert leaf.destruction_time == math.inf


def test_assign_trie_destruction_time_youngestplus1_2():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner1 = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    inner2 = impl.TrieInnerNode(rank=2, differentia=10, parent=inner1)
    leaf = impl.TrieLeafNode(parent=inner2, taxon_label="A")
    root = hstrat.CompoundTriePostprocessor(
        [
            hstrat.AssignOriginTimeNaiveTriePostprocessor(),
            hstrat.AssignDestructionTimeYoungestPlusOneTriePostprocessor(),
        ],
    )(root, p_differentia_collision=0.5, mutate=True)
    assert root.destruction_time == 1.5
    assert inner1.destruction_time == 3
    assert inner2.destruction_time == 3
    assert leaf.destruction_time == math.inf


def test_assign_trie_destruction_time_youngestplus1_3():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner1 = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    inner2 = impl.TrieInnerNode(rank=3, differentia=10, parent=inner1)
    leaf = impl.TrieLeafNode(parent=inner2, taxon_label="A")
    root = hstrat.CompoundTriePostprocessor(
        [
            hstrat.AssignOriginTimeNaiveTriePostprocessor(),
            hstrat.AssignDestructionTimeYoungestPlusOneTriePostprocessor(),
        ],
    )(root, p_differentia_collision=0.5, mutate=True)
    assert root.destruction_time == 2
    assert inner1.destruction_time == 4
    assert inner2.destruction_time == 4
    assert leaf.destruction_time == math.inf


def test_assign_trie_destruction_time_youngestplus1_complex():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner1 = impl.TrieInnerNode(rank=0, differentia=0, parent=root)

    inner2 = impl.TrieInnerNode(rank=4, differentia=10, parent=inner1)
    inner3 = impl.TrieInnerNode(rank=7, differentia=7, parent=inner2)

    inner2a = impl.TrieInnerNode(rank=1, differentia=1, parent=inner1)

    leaf3_a = impl.TrieLeafNode(parent=inner3, taxon_label="leaf3a_a")

    leaf2a_a = impl.TrieLeafNode(parent=inner2a, taxon_label="leaf2a_a")
    leaf2a_b = impl.TrieLeafNode(parent=inner2a, taxon_label="leaf2a_b")

    root = hstrat.CompoundTriePostprocessor(
        [
            hstrat.AssignOriginTimeNaiveTriePostprocessor(),
            hstrat.AssignDestructionTimeYoungestPlusOneTriePostprocessor(),
        ],
    )(root, p_differentia_collision=0.5, mutate=True)

    assert root.destruction_time == 1
    assert inner1.destruction_time == 2
    assert inner2.destruction_time == 8
    assert inner3.destruction_time == 8
    assert inner2a.destruction_time == 2
    assert leaf2a_a.destruction_time == math.inf
    assert leaf2a_b.destruction_time == math.inf
    assert leaf3_a.destruction_time == math.inf


def test_assign_trie_destruction_time_youngestplus1_assigned_property():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    leaf = impl.TrieLeafNode(parent=inner, taxon_label="A")
    root = hstrat.CompoundTriePostprocessor(
        [
            hstrat.AssignOriginTimeNaiveTriePostprocessor(),
            hstrat.AssignDestructionTimeYoungestPlusOneTriePostprocessor(
                assigned_property="blueberry"
            ),
        ],
    )(root, p_differentia_collision=0.5, mutate=True)
    assert leaf.blueberry == math.inf
    assert inner.blueberry == 1
    assert root.blueberry == 1


def test_assign_trie_destruction_time_youngestplus1_origin_time_property():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    leaf = impl.TrieLeafNode(parent=inner, taxon_label="A")
    root = hstrat.CompoundTriePostprocessor(
        [
            hstrat.AssignOriginTimeNaiveTriePostprocessor(
                assigned_property="blueberry"
            ),
            hstrat.AssignDestructionTimeYoungestPlusOneTriePostprocessor(
                origin_time_property="blueberry"
            ),
        ]
    )(root, p_differentia_collision=0.5, mutate=True)
    assert leaf.destruction_time == math.inf
    assert inner.destruction_time == 1
    assert root.destruction_time == 1


def test_assign_trie_destruction_time_youngestplus1_otime_and_aprop():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    leaf = impl.TrieLeafNode(parent=inner, taxon_label="A")
    root = hstrat.CompoundTriePostprocessor(
        [
            hstrat.AssignOriginTimeNaiveTriePostprocessor(
                assigned_property="blueberry"
            ),
            hstrat.AssignDestructionTimeYoungestPlusOneTriePostprocessor(
                origin_time_property="blueberry", assigned_property="raspberry"
            ),
        ],
    )(root, p_differentia_collision=0.5, mutate=True)
    assert leaf.raspberry == math.inf
    assert inner.raspberry == 1
    assert root.raspberry == 1


def test_assign_trie_destruction_time_youngestplus1_mutate():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    leaf = impl.TrieLeafNode(parent=inner, taxon_label="A")
    root_ = hstrat.CompoundTriePostprocessor(
        [
            hstrat.AssignOriginTimeNaiveTriePostprocessor(),
            hstrat.AssignDestructionTimeYoungestPlusOneTriePostprocessor(
                assigned_property="blueberry"
            ),
        ],
    )(root, p_differentia_collision=0.5, mutate=False)
    assert not hasattr(leaf, "blueberry")
    assert not hasattr(inner, "blueberry")
    assert not hasattr(root, "blueberry")

    assert hasattr(root_, "blueberry")

    root = hstrat.CompoundTriePostprocessor(
        [
            hstrat.AssignOriginTimeNaiveTriePostprocessor(),
            hstrat.AssignDestructionTimeYoungestPlusOneTriePostprocessor(
                assigned_property="blueberry"
            ),
        ],
    )(root, p_differentia_collision=0.5, mutate=True)
    assert str(anytree.RenderTree(root).by_attr("blueberry")) == str(
        anytree.RenderTree(root_).by_attr("blueberry")
    )
