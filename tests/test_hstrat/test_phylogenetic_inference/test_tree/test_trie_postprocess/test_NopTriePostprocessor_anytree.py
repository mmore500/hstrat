import anytree

from hstrat import hstrat
import hstrat.phylogenetic_inference.tree._impl as impl
import hstrat.phylogenetic_inference.tree.trie_postprocess._detail as detail


def test_base_class():
    assert issubclass(
        hstrat.NopTriePostprocessor,
        detail.TriePostprocessorBase,
    )


def test_nop_mutate():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    inner = impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    _leaf = impl.TrieLeafNode(parent=inner, taxon_label="A")
    root_ = hstrat.NopTriePostprocessor()(
        root, p_differentia_collision=0.5, mutate=False
    )
    assert root is not root_
    assert str(anytree.RenderTree(root).by_attr("id")) == str(
        anytree.RenderTree(root_).by_attr("id"),
    )

    root = hstrat.NopTriePostprocessor()(
        root, p_differentia_collision=0.5, mutate=True
    )
    assert str(anytree.RenderTree(root).by_attr("id")) == str(
        anytree.RenderTree(root_).by_attr("id"),
    )
