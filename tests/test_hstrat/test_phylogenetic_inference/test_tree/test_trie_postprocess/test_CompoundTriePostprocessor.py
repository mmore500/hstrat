from hstrat import hstrat
import hstrat.phylogenetic_inference.tree._impl as impl


def test_empty():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    leaf = impl.TrieLeafNode(parent=inner, taxon_label="A")
    root = hstrat.CompoundTriePostprocessor([])(
        root, p_differentia_collision=0.5, mutate=True
    )
    assert not hasattr(leaf, "origin_time")
    assert not hasattr(inner, "origin_time")
    assert not hasattr(root, "origin_time")
    assert not hasattr(leaf, "blueberry")
    assert not hasattr(inner, "blueberry")
    assert not hasattr(root, "blueberry")


def test_singleton():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    leaf = impl.TrieLeafNode(parent=inner, taxon_label="A")
    root = hstrat.CompoundTriePostprocessor(
        [
            hstrat.AssignOriginTimeNodeRankTriePostprocessor(),
        ]
    )(root, p_differentia_collision=0.5, mutate=True)
    assert getattr(leaf, "origin_time") == 0
    assert getattr(inner, "origin_time") == 0
    assert getattr(root, "origin_time") == 0
    assert not hasattr(leaf, "blueberry")
    assert not hasattr(inner, "blueberry")
    assert not hasattr(root, "blueberry")


def test_pair():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    leaf = impl.TrieLeafNode(parent=inner, taxon_label="A")
    root = hstrat.CompoundTriePostprocessor(
        [
            hstrat.AssignOriginTimeNodeRankTriePostprocessor(),
            hstrat.AssignOriginTimeNodeRankTriePostprocessor(
                assigned_property="blueberry"
            ),
        ]
    )(root, p_differentia_collision=0.5, mutate=True)
    assert getattr(leaf, "origin_time") == 0
    assert getattr(inner, "origin_time") == 0
    assert getattr(root, "origin_time") == 0
    assert getattr(leaf, "blueberry") == 0
    assert getattr(inner, "blueberry") == 0
    assert getattr(root, "blueberry") == 0


def test_mutate():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    leaf = impl.TrieLeafNode(parent=inner, taxon_label="A")

    processed_root = hstrat.CompoundTriePostprocessor(
        [
            hstrat.AssignOriginTimeNodeRankTriePostprocessor(),
            hstrat.AssignOriginTimeNodeRankTriePostprocessor(
                assigned_property="blueberry"
            ),
        ]
    )(root, p_differentia_collision=0.5, mutate=False)
    assert not hasattr(leaf, "origin_time")
    assert not hasattr(inner, "origin_time")
    assert not hasattr(root, "origin_time")
    assert not hasattr(leaf, "blueberry")
    assert not hasattr(inner, "blueberry")
    assert not hasattr(root, "blueberry")

    assert hasattr(processed_root, "origin_time")
    assert hasattr(processed_root, "blueberry")
