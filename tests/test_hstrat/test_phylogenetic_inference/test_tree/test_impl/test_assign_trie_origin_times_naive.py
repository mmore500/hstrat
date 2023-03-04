import numpy as np
import pytest

import hstrat.phylogenetic_inference.tree._impl as impl


def test_assign_trie_origin_times_naive_single_leaf():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    leaf = impl.TrieLeafNode(parent=inner, taxon_label="A")
    impl.assign_trie_origin_times_naive(root)
    assert leaf.origin_time == 0
    assert inner.origin_time == 0
    assert root.origin_time == 0


def test_assign_trie_origin_times_naive_two_leaves():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    leaf1 = impl.TrieLeafNode(parent=inner, taxon_label="A")
    leaf2 = impl.TrieLeafNode(parent=inner, taxon_label="B")
    impl.assign_trie_origin_times_naive(root)
    assert root.origin_time == 0
    assert inner.origin_time == 0
    assert leaf1.origin_time == 0
    assert leaf2.origin_time == 0


def test_assign_trie_origin_times_naive1():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner1 = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    inner2 = impl.TrieInnerNode(rank=1, differentia=10, parent=inner1)
    leaf = impl.TrieLeafNode(parent=inner2, taxon_label="A")
    impl.assign_trie_origin_times_naive(root)
    assert root.origin_time == 0
    assert inner1.origin_time == 0
    assert inner2.origin_time == 1
    assert leaf.origin_time == 1


def test_assign_trie_origin_times_naive2():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner1 = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    inner2 = impl.TrieInnerNode(rank=2, differentia=10, parent=inner1)
    leaf = impl.TrieLeafNode(parent=inner2, taxon_label="A")
    impl.assign_trie_origin_times_naive(root)
    assert root.origin_time == 0
    assert inner1.origin_time == 0.5
    assert inner2.origin_time == 2
    assert leaf.origin_time == 2


def test_assign_trie_origin_times_naive3():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner1 = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    inner2 = impl.TrieInnerNode(rank=3, differentia=10, parent=inner1)
    leaf = impl.TrieLeafNode(parent=inner2, taxon_label="A")
    impl.assign_trie_origin_times_naive(root)
    assert root.origin_time == 0
    assert inner1.origin_time == 1
    assert inner2.origin_time == 3
    assert leaf.origin_time == 3


def test_assign_trie_origin_times_naive_complex():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner1 = impl.TrieInnerNode(rank=0, differentia=0, parent=root)

    inner2 = impl.TrieInnerNode(rank=4, differentia=10, parent=inner1)
    inner3 = impl.TrieInnerNode(rank=7, differentia=7, parent=inner2)

    inner2a = impl.TrieInnerNode(rank=1, differentia=1, parent=inner1)

    leaf3_a = impl.TrieLeafNode(parent=inner3, taxon_label="leaf3a_a")

    leaf2a_a = impl.TrieLeafNode(parent=inner2a, taxon_label="leaf2a_a")
    leaf2a_b = impl.TrieLeafNode(parent=inner2a, taxon_label="leaf2a_b")

    impl.assign_trie_origin_times_naive(root)

    assert root.origin_time == 0
    assert inner1.origin_time == 0
    assert inner2.origin_time == 5
    assert inner3.origin_time == 7
    assert inner2a.origin_time == 1
    assert leaf2a_a.origin_time == 1
    assert leaf2a_b.origin_time == 1
    assert leaf3_a.origin_time == 7


def test_assign_trie_origin_times_naive_assigned_property():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    leaf = impl.TrieLeafNode(parent=inner, taxon_label="A")
    impl.assign_trie_origin_times_naive(root, "blueberry")
    assert leaf.blueberry == 0
    assert inner.blueberry == 0
    assert root.blueberry == 0
