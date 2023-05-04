import copy

import anytree
from keyname import keyname as kn
import pytest

from hstrat import hstrat
from hstrat._auxiliary_lib import anytree_cardinality
import hstrat.phylogenetic_inference.tree._impl as impl


@pytest.fixture
def trie():
    # (rank None, diff None) @ B6A
    # └── (rank 0, diff 2) @ BtQ
    #     ├── (rank 3, diff 31) @ jg
    #     |   └── space @ 0B
    #     └── (rank 3, diff 1) @ BUQ
    #         ├── spice @ 0A
    #         ├── sweet @ xA
    #         ├── (rank 4, diff 17) @ BxA
    #         │   └── (rank 5, diff 11) @ Gg
    #         │       ├── (rank 6, diff 19) @ Biw
    #         │       |  └── bank @ B-Q
    #         │       └── (rank 6, diff 21) @ HA
    #         │           └── baa @ B-Q
    #         ├── (rank 4, diff 16) @ B7Q
    #         │   └── (rank 5, diff 11) @ sA
    #         │       └── foo @ BtQ
    #         └── (rank 4, diff 17) @ Brw
    #             ├── (rank 6, diff 19) @ BLg
    #             │   ├── bump @ B0g
    #             │   ├── baz @ B0g
    #             │   └── barf @ 901
    #             └── (rank 6, diff 19) @ BoA
    #                 └── bar @ B8A

    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    genesis_node = impl.TrieInnerNode(rank=0, differentia=2, parent=root)
    sibling_node = impl.TrieInnerNode(
        rank=3, differentia=31, parent=genesis_node
    )
    impl.TrieLeafNode(sibling_node, "space")
    focal_node = impl.TrieInnerNode(rank=3, differentia=1, parent=genesis_node)
    impl.TrieLeafNode(focal_node, "spice")
    impl.TrieLeafNode(focal_node, "sweet")
    child1 = impl.TrieInnerNode(rank=4, differentia=17, parent=focal_node)
    child2 = impl.TrieInnerNode(rank=4, differentia=16, parent=focal_node)
    child3 = impl.TrieInnerNode(rank=4, differentia=17, parent=focal_node)
    grandchild1 = impl.TrieInnerNode(rank=5, differentia=11, parent=child1)
    grandchild2 = impl.TrieInnerNode(rank=5, differentia=11, parent=child2)
    impl.TrieLeafNode(grandchild2, "foo")
    greatgrandchild0 = impl.TrieInnerNode(
        rank=6, differentia=19, parent=grandchild1
    )
    impl.TrieLeafNode(greatgrandchild0, "bank")
    greatgrandchild1 = impl.TrieInnerNode(
        rank=6, differentia=21, parent=grandchild1
    )
    impl.TrieLeafNode(greatgrandchild1, "baa")
    greatgrandchild2 = impl.TrieInnerNode(
        rank=6, differentia=19, parent=child3
    )
    impl.TrieLeafNode(greatgrandchild2, "bump")
    impl.TrieLeafNode(greatgrandchild2, "baz")
    impl.TrieLeafNode(greatgrandchild2, "barf")
    greatgrandchild3 = impl.TrieInnerNode(
        rank=6, differentia=19, parent=child3
    )
    impl.TrieLeafNode(greatgrandchild3, "bar")

    return root


def test_singleton():
    root_node = impl.TrieInnerNode(rank=None, differentia=None)
    inner_node = impl.TrieInnerNode(rank=1, differentia=2, parent=root_node)
    impl.TrieLeafNode(taxon_label="bar", parent=inner_node)

    processed_root = hstrat.PeelBackConjoinedLeavesTriePostprocessor()(
        root_node,
        p_differentia_collision=0.25,
        mutate=False,
    )
    assert str(
        anytree.RenderTree(processed_root).by_attr("taxon_label")
    ) == str(anytree.RenderTree(root_node).by_attr("taxon_label"))


def test_twins():
    root_node = impl.TrieInnerNode(rank=None, differentia=None)
    root_node.test_name = "root"
    inner_node = impl.TrieInnerNode(rank=0, differentia=2, parent=root_node)
    inner_node.test_name = "inner"
    leaf_node1 = impl.TrieLeafNode(taxon_label="bar", parent=inner_node)
    leaf_node1.test_name = "leaf_bar"
    leaf_node2 = impl.TrieLeafNode(taxon_label="baz", parent=inner_node)
    leaf_node2.test_name = "leaf_baz"

    expected_root = impl.TrieInnerNode(rank=None, differentia=None)
    expected_root.test_name = "root"
    expected_inner1 = impl.TrieInnerNode(
        rank=0, differentia=2, parent=expected_root
    )
    expected_inner1.test_name = "inner"
    expected_inner2 = impl.TrieInnerNode(
        rank=0, differentia=2, parent=expected_root
    )
    expected_inner2.test_name = "inner"
    leaf_node1 = impl.TrieLeafNode(taxon_label="baz", parent=expected_inner1)
    leaf_node1.test_name = "leaf_baz"
    leaf_node2 = impl.TrieLeafNode(taxon_label="bar", parent=expected_inner2)
    leaf_node2.test_name = "leaf_bar"

    processed_root = hstrat.PeelBackConjoinedLeavesTriePostprocessor()(
        root_node,
        p_differentia_collision=0.25,
        mutate=False,
    )
    assert str(
        anytree.RenderTree(processed_root).by_attr("taxon_label")
    ) != str(anytree.RenderTree(root_node).by_attr("taxon_label"))
    assert str(anytree.RenderTree(processed_root).by_attr("test_name")) == str(
        anytree.RenderTree(expected_root).by_attr("test_name")
    )


def test_mutate(trie):
    root_node = impl.TrieInnerNode(rank=None, differentia=None)
    inner_node = impl.TrieInnerNode(rank=0, differentia=2, parent=root_node)
    impl.TrieLeafNode(taxon_label="bar", parent=inner_node)
    impl.TrieLeafNode(taxon_label="baz", parent=inner_node)

    root_bak = copy.deepcopy(root_node)

    hstrat.PeelBackConjoinedLeavesTriePostprocessor()(
        root_node,
        p_differentia_collision=0.25,
        mutate=False,
    )

    assert str(anytree.RenderTree(root_bak).by_attr("taxon_label")) == str(
        anytree.RenderTree(root_node).by_attr("taxon_label")
    )


def test_fixture(trie):
    cardinality_before = anytree_cardinality(trie)
    leaf_cardinality_before = len(trie.leaves)
    processed_trie = hstrat.PeelBackConjoinedLeavesTriePostprocessor()(
        trie,
        p_differentia_collision=0.25,
        mutate=False,
    )

    assert anytree_cardinality(processed_trie) == cardinality_before + 3

    assert len(trie.leaves) == leaf_cardinality_before
    for leaf in processed_trie.leaves:
        assert sum(1 for __ in leaf.parent.outer_children) == 1

    for leaf_taxon in "bump", "baz", "barf":
        leaf_node = next(
            node
            for node in anytree.PostOrderIter(processed_trie)
            if node.taxon_label == leaf_taxon
        )
        assert len(leaf_node.parent.children) == 1
        assert leaf_node.parent.IsAnOriginationOfAllele(rank=6, differentia=19)
        assert len(leaf_node.parent.parent.children) == 4

    for leaf_taxon in "spice", "sweet":
        leaf_node = next(
            node
            for node in anytree.PostOrderIter(processed_trie)
            if node.taxon_label == leaf_taxon
        )
        assert leaf_node.parent.IsAnOriginationOfAllele(rank=3, differentia=1)

    for node in anytree.PostOrderIter(processed_trie):
        attrs = kn.unpack(node.taxon_label)
        if "uid" in attrs:
            del attrs["uid"]
        node.test_name = kn.pack(attrs).rstrip("=")
        node.children = sorted(node.children, key=lambda x: x.test_name)

    assert str(anytree.RenderTree(processed_trie).by_attr("test_name")) == (
        """Root
└── Inner=+d=C+r=0
    ├── Inner=+d=B+r=3
    │   ├── Inner=+d=Q+r=4
    │   │   └── Inner=+d=L+r=5
    │   │       └── foo
    │   ├── Inner=+d=R+r=4
    │   │   └── Inner=+d=L+r=5
    │   │       ├── Inner=+d=T+r=6
    │   │       │   └── bank
    │   │       └── Inner=+d=V+r=6
    │   │           └── baa
    │   ├── Inner=+d=R+r=4
    │   │   ├── Inner=+d=T+r=6
    │   │   │   └── barf
    │   │   ├── Inner=+d=T+r=6
    │   │   │   └── bar
    │   │   ├── Inner=+d=T+r=6
    │   │   │   └── bump
    │   │   └── Inner=+d=T+r=6
    │   │       └── baz
    │   └── sweet
    ├── Inner=+d=B+r=3
    │   └── spice
    └── Inner=+d=f+r=3
        └── space"""
    )
