import math

import anytree

from hstrat import hstrat
import hstrat.phylogenetic_inference.tree._impl as impl
import hstrat.phylogenetic_inference.tree.trie_postprocess._detail as detail


def test_base_class():
    assert issubclass(
        hstrat.AssignOriginTimeExpectedValueTriePostprocessor,
        detail.TriePostprocessorBase,
    )


def test_assign_trie_origin_times_expected_value_single_leaf__arbitrary():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    leaf = impl.TrieLeafNode(parent=inner, taxon_label="A")
    root = hstrat.AssignOriginTimeExpectedValueTriePostprocessor(
        prior=hstrat.ArbitraryPrior()
    )(root, p_differentia_collision=0.25, mutate=True)
    assert leaf.origin_time == 0
    assert inner.origin_time == 0
    assert root.origin_time == 0


def test_assign_trie_origin_times_expected_value_single_leaf__assigned_property():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    leaf = impl.TrieLeafNode(parent=inner, taxon_label="A")
    root = hstrat.AssignOriginTimeExpectedValueTriePostprocessor(
        prior=hstrat.ArbitraryPrior(),
        assigned_property="raspberry",
    )(root, p_differentia_collision=0.25, mutate=True)
    assert leaf.raspberry == 0
    assert inner.raspberry == 0
    assert root.raspberry == 0


def test_assign_trie_origin_times_expected_value_two_leaves__arbitrary():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    leaf1 = impl.TrieLeafNode(parent=inner, taxon_label="A")
    leaf2 = impl.TrieLeafNode(parent=inner, taxon_label="B")
    root = hstrat.AssignOriginTimeExpectedValueTriePostprocessor(
        prior=hstrat.ArbitraryPrior()
    )(root, p_differentia_collision=0.25, mutate=True)
    assert root.origin_time == 0
    assert inner.origin_time == 0
    assert leaf1.origin_time == 0
    assert leaf2.origin_time == 0


def test_assign_trie_origin_times_expected_value1__arbitrary():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner1 = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    inner2 = impl.TrieInnerNode(rank=1, differentia=10, parent=inner1)
    leaf = impl.TrieLeafNode(parent=inner2, taxon_label="A")
    root = hstrat.AssignOriginTimeExpectedValueTriePostprocessor(
        prior=hstrat.ArbitraryPrior()
    )(root, p_differentia_collision=0.25, mutate=True)
    assert root.origin_time == 0
    assert inner1.origin_time == 0
    assert inner2.origin_time == (1 + 0) / (1 + 0.25)
    assert leaf.origin_time == 1


def test_assign_trie_origin_times_expected_value2__arbitrary():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner1 = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    inner2 = impl.TrieInnerNode(rank=2, differentia=10, parent=inner1)
    leaf = impl.TrieLeafNode(parent=inner2, taxon_label="A")
    root = hstrat.AssignOriginTimeExpectedValueTriePostprocessor(
        prior=hstrat.ArbitraryPrior()
    )(root, p_differentia_collision=0.25, mutate=True)
    assert root.origin_time == 0
    assert math.isclose(inner1.origin_time, (0.5 + 0 * 0.25) / (1 + 0.25))
    assert math.isclose(
        inner2.origin_time, (2 + inner1.origin_time * 0.25) / (1 + 0.25)
    )
    assert leaf.origin_time == 2


def test_assign_trie_origin_times_expected_value3__arbitrary():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner1 = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    inner2 = impl.TrieInnerNode(rank=3, differentia=10, parent=inner1)
    leaf = impl.TrieLeafNode(parent=inner2, taxon_label="A")
    root = hstrat.AssignOriginTimeExpectedValueTriePostprocessor(
        prior=hstrat.ArbitraryPrior()
    )(root, p_differentia_collision=0.25, mutate=True)
    assert root.origin_time == 0
    assert math.isclose(inner1.origin_time, (1 + 0 * 0.25) / (1 + 0.25))
    assert math.isclose(
        inner2.origin_time, (3 + inner1.origin_time * 0.25) / (1 + 0.25)
    )
    assert leaf.origin_time == 3


def test_assign_trie_origin_times_expected_value_complex__arbitrary():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner1 = impl.TrieInnerNode(rank=0, differentia=0, parent=root)

    inner2 = impl.TrieInnerNode(rank=4, differentia=10, parent=inner1)
    inner3 = impl.TrieInnerNode(rank=7, differentia=7, parent=inner2)

    inner2a = impl.TrieInnerNode(rank=1, differentia=1, parent=inner1)

    leaf3_a = impl.TrieLeafNode(parent=inner3, taxon_label="leaf3a_a")

    impl.TrieLeafNode(parent=inner2a, taxon_label="leaf2a_a")
    leaf2a_b = impl.TrieLeafNode(parent=inner2a, taxon_label="leaf2a_b")

    root = hstrat.AssignOriginTimeExpectedValueTriePostprocessor(
        prior=hstrat.ArbitraryPrior()
    )(root, p_differentia_collision=0.25, mutate=True)

    assert root.origin_time == 0
    assert math.isclose(inner1.origin_time, (0 + 0 * 0.25) / 1.25)
    assert math.isclose(
        inner2.origin_time, (5 + inner1.origin_time * 0.25) / 1.25
    )
    assert math.isclose(
        inner3.origin_time, (7 + inner2.origin_time * 0.25) / 1.25
    )
    assert math.isclose(
        inner2a.origin_time, (1 + inner1.origin_time * 0.25) / 1.25
    )
    assert leaf2a_b.origin_time == 1
    assert leaf3_a.origin_time == 7


def test_assign_trie_origin_times_expected_value_single_leaf__uniform():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    leaf = impl.TrieLeafNode(parent=inner, taxon_label="A")
    root = hstrat.AssignOriginTimeExpectedValueTriePostprocessor(
        prior=hstrat.UniformPrior()
    )(root, p_differentia_collision=0.25, mutate=True)
    assert leaf.origin_time == 0
    assert inner.origin_time == 0
    assert root.origin_time == 0


def test_assign_trie_origin_times_expected_value_two_leaves__uniform():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    leaf1 = impl.TrieLeafNode(parent=inner, taxon_label="A")
    leaf2 = impl.TrieLeafNode(parent=inner, taxon_label="B")
    root = hstrat.AssignOriginTimeExpectedValueTriePostprocessor(
        prior=hstrat.UniformPrior()
    )(root, p_differentia_collision=0.25, mutate=True)
    assert root.origin_time == 0
    assert inner.origin_time == 0
    assert leaf1.origin_time == 0
    assert leaf2.origin_time == 0


def test_assign_trie_origin_times_expected_value1__uniform():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner1 = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    inner2 = impl.TrieInnerNode(rank=1, differentia=10, parent=inner1)
    leaf = impl.TrieLeafNode(parent=inner2, taxon_label="A")
    root = hstrat.AssignOriginTimeExpectedValueTriePostprocessor(
        prior=hstrat.UniformPrior()
    )(root, p_differentia_collision=0.25, mutate=True)
    assert root.origin_time == 0
    assert inner1.origin_time == 0
    assert inner2.origin_time == (1 + 0) / (1 + 0.25)
    assert leaf.origin_time == 1


def test_assign_trie_origin_times_expected_value2__uniform():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner1 = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    inner2 = impl.TrieInnerNode(rank=2, differentia=10, parent=inner1)
    leaf = impl.TrieLeafNode(parent=inner2, taxon_label="A")
    root = hstrat.AssignOriginTimeExpectedValueTriePostprocessor(
        prior=hstrat.UniformPrior()
    )(root, p_differentia_collision=0.25, mutate=True)
    assert root.origin_time == 0
    assert math.isclose(
        inner1.origin_time, (2 * 0.5 + 0 * 0.25) / (2 * 1 + 1 * 0.25)
    )
    assert math.isclose(
        inner2.origin_time, (2 + inner1.origin_time * 0.25) / (1 + 0.25)
    )
    assert leaf.origin_time == 2


def test_assign_trie_origin_times_expected_value3__uniform():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner1 = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    inner2 = impl.TrieInnerNode(rank=3, differentia=10, parent=inner1)
    leaf = impl.TrieLeafNode(parent=inner2, taxon_label="A")
    root = hstrat.AssignOriginTimeExpectedValueTriePostprocessor(
        prior=hstrat.UniformPrior()
    )(root, p_differentia_collision=0.25, mutate=True)
    assert root.origin_time == 0
    assert math.isclose(
        inner1.origin_time, (3 * 1 + 0 * 0.25) / (3 * 1 + 0.25)
    )
    assert math.isclose(
        inner2.origin_time, (3 + inner1.origin_time * 0.25) / (1 + 0.25)
    )
    assert leaf.origin_time == 3


def test_assign_trie_origin_times_expected_value4__uniform():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner1 = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    inner2 = impl.TrieInnerNode(rank=3, differentia=10, parent=inner1)
    inner3 = impl.TrieInnerNode(rank=6, differentia=10, parent=inner2)
    leaf = impl.TrieLeafNode(parent=inner3, taxon_label="A")
    root = hstrat.AssignOriginTimeExpectedValueTriePostprocessor(
        prior=hstrat.UniformPrior()
    )(root, p_differentia_collision=0.25, mutate=True)
    assert root.origin_time == 0
    assert math.isclose(
        inner1.origin_time, (3 * 1 + 0 * 0.25) / (3 * 1 + 0.25)
    )
    expected = (3 * 4 + inner1.origin_time * 0.25) / (3 * 1 + 0.25)
    assert math.isclose(inner2.origin_time, expected)
    assert leaf.origin_time == 6


def test_assign_trie_origin_times_expected_value3__uniform_fork():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner1 = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    inner2 = impl.TrieInnerNode(rank=3, differentia=10, parent=inner1)
    inner2b = impl.TrieInnerNode(rank=300, differentia=11, parent=inner1)
    inner3b = impl.TrieInnerNode(rank=309, differentia=12, parent=inner2b)
    leaf = impl.TrieLeafNode(parent=inner2, taxon_label="A")
    leafb = impl.TrieLeafNode(parent=inner3b, taxon_label="X")
    root = hstrat.AssignOriginTimeExpectedValueTriePostprocessor(
        prior=hstrat.UniformPrior()
    )(root, p_differentia_collision=0.25, mutate=True)
    assert root.origin_time == 0
    assert math.isclose(
        inner1.origin_time, (3 * 1 + 0 * 0.25) / (3 * 1 + 0.25)
    )
    assert math.isclose(
        inner2.origin_time, (3 + inner1.origin_time * 0.25) / (1 + 0.25)
    )
    assert leaf.origin_time == 3
    expected = (304 * 9 + inner1.origin_time * 0.25) / (1 * 9 + 0.25)
    assert math.isclose(inner2b.origin_time, expected)
    expected = (309 + inner2b.origin_time * 0.25) / (1 + 0.25)
    assert math.isclose(inner3b.origin_time, expected)
    assert leafb.origin_time == 309


def test_assign_trie_origin_times_naive_mutate():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner1 = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    inner2 = impl.TrieInnerNode(rank=1, differentia=10, parent=inner1)
    leaf = impl.TrieLeafNode(parent=inner2, taxon_label="A")
    root_ = hstrat.AssignOriginTimeNaiveTriePostprocessor(
        prior=hstrat.ArbitraryPrior(),
        assigned_property="raspberry",
    )(root, p_differentia_collision=0.5, mutate=False)
    assert not hasattr(leaf, "raspberry")
    assert not hasattr(inner1, "raspberry")
    assert not hasattr(inner2, "raspberry")
    assert not hasattr(root, "raspberry")

    assert hasattr(root_, "raspberry")
    root = hstrat.AssignOriginTimeNaiveTriePostprocessor(
        prior=hstrat.ArbitraryPrior(),
        assigned_property="raspberry",
    )(root, p_differentia_collision=0.5, mutate=True)

    assert str(anytree.RenderTree(root).by_attr("raspberry")) == str(
        anytree.RenderTree(root_).by_attr("raspberry")
    )
