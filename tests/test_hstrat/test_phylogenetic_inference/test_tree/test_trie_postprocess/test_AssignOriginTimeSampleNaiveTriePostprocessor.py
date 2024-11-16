import anytree
import networkx as nx
import pytest

from hstrat import hstrat
from hstrat._auxiliary_lib import random_tree, seed_random
import hstrat.phylogenetic_inference.tree._impl as impl
import hstrat.phylogenetic_inference.tree.trie_postprocess._detail as detail


def test_base_class():
    assert issubclass(
        hstrat.AssignOriginTimeSampleNaiveTriePostprocessor,
        detail.TriePostprocessorBase,
    )


def test_assign_trie_origin_times_naive_single_leaf():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    leaf = impl.TrieLeafNode(parent=inner, taxon_label="A")
    root = hstrat.AssignOriginTimeSampleNaiveTriePostprocessor()(
        root, p_differentia_collision=0.5, mutate=True
    )
    assert leaf.origin_time == 0
    assert inner.origin_time == 0
    assert root.origin_time == 0


def test_assign_trie_origin_times_naive_two_leaves():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    leaf1 = impl.TrieLeafNode(parent=inner, taxon_label="A")
    leaf2 = impl.TrieLeafNode(parent=inner, taxon_label="B")
    root = hstrat.AssignOriginTimeSampleNaiveTriePostprocessor()(
        root, p_differentia_collision=0.5, mutate=True
    )
    assert root.origin_time == 0
    assert inner.origin_time == 0
    assert leaf1.origin_time == 0
    assert leaf2.origin_time == 0


def test_assign_trie_origin_times_naive1():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner1 = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    inner2 = impl.TrieInnerNode(rank=1, differentia=10, parent=inner1)
    leaf = impl.TrieLeafNode(parent=inner2, taxon_label="A")
    root = hstrat.AssignOriginTimeSampleNaiveTriePostprocessor()(
        root, p_differentia_collision=0.5, mutate=True
    )
    assert root.origin_time == 0
    assert inner1.origin_time == 0
    assert 0 <= inner2.origin_time <= 1
    assert leaf.origin_time == 1


def test_assign_trie_origin_times_naive2():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner1 = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    inner2 = impl.TrieInnerNode(rank=2, differentia=10, parent=inner1)
    leaf = impl.TrieLeafNode(parent=inner2, taxon_label="A")
    root = hstrat.AssignOriginTimeSampleNaiveTriePostprocessor()(
        root, p_differentia_collision=0.5, mutate=True
    )
    assert root.origin_time == 0
    assert 0 <= inner1.origin_time <= 0.5
    assert 0.5 <= inner2.origin_time <= 2
    assert leaf.origin_time == 2


def test_assign_trie_origin_times_naive3():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner1 = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    inner2 = impl.TrieInnerNode(rank=3, differentia=10, parent=inner1)
    leaf = impl.TrieLeafNode(parent=inner2, taxon_label="A")
    root = hstrat.AssignOriginTimeSampleNaiveTriePostprocessor()(
        root, p_differentia_collision=0.5, mutate=True
    )
    assert root.origin_time == 0
    assert 0 <= inner1.origin_time <= 2
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

    root = hstrat.AssignOriginTimeNaiveTriePostprocessor()(
        root, p_differentia_collision=0.5, mutate=True
    )

    assert root.origin_time == 0
    assert inner1.origin_time == 0
    assert 4 <= inner2.origin_time <= 6
    assert inner3.origin_time == 7
    assert inner2a.origin_time == 1
    assert leaf2a_a.origin_time == 1
    assert leaf2a_b.origin_time == 1
    assert leaf3_a.origin_time == 7


def test_assign_trie_origin_times_naive_assigned_property():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    leaf = impl.TrieLeafNode(parent=inner, taxon_label="A")
    root = hstrat.AssignOriginTimeSampleNaiveTriePostprocessor(
        assigned_property="blueberry"
    )(root, p_differentia_collision=0.5, mutate=True)
    assert leaf.blueberry == 0
    assert inner.blueberry == 0
    assert root.blueberry == 0


def test_assign_trie_origin_times_naive_mutate():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    leaf = impl.TrieLeafNode(parent=inner, taxon_label="A")
    root_ = hstrat.AssignOriginTimeSampleNaiveTriePostprocessor(
        assigned_property="blueberry"
    )(root, p_differentia_collision=0.5, mutate=False)
    assert not hasattr(leaf, "blueberry")
    assert not hasattr(inner, "blueberry")
    assert not hasattr(root, "blueberry")

    assert hasattr(root_, "blueberry")

    root = hstrat.AssignOriginTimeSampleNaiveTriePostprocessor(
        prior=hstrat.ArbitraryPrior(),
        assigned_property="blueberry",
    )(root, p_differentia_collision=0.5, mutate=True)
    assert str(anytree.RenderTree(root).by_attr("blueberry")) == str(
        anytree.RenderTree(root_).by_attr("blueberry")
    )


@pytest.mark.parametrize("tree_size", [300])
@pytest.mark.parametrize("differentia_width", [64])
@pytest.mark.parametrize("tree_seed", range(10))
@pytest.mark.parametrize(
    "retention_policy", [hstrat.perfect_resolution_algo.Policy()]
)
def test_perfect_rank_equivalence(
    tree_seed, tree_size, differentia_width, retention_policy
):
    seed_random(tree_seed)
    nx_tree = random_tree(n=tree_size, seed=tree_seed, create_using=nx.DiGraph)

    extant_population = hstrat.descend_template_phylogeny_networkx(
        nx_tree,
        seed_column=hstrat.HereditaryStratigraphicColumn(
            stratum_retention_policy=retention_policy,
            stratum_differentia_bit_width=differentia_width,
        ),
    )

    rank_df, naive_df = hstrat.build_tree_trie_ensemble(
        extant_population,
        trie_postprocessors=[
            hstrat.AssignOriginTimeNodeRankTriePostprocessor(),
            hstrat.AssignOriginTimeSampleNaiveTriePostprocessor(),
        ],
    )

    assert (rank_df["origin_time"] == naive_df["origin_time"]).all()
