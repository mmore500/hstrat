import anytree
import networkx as nx
import pytest

from hstrat import hstrat
from hstrat._auxiliary_lib import (
    AnyTreeAscendingIter,
    anytree_cardinality,
    random_tree,
    seed_random,
)
import hstrat.phylogenetic_inference.tree._impl as impl
import hstrat.phylogenetic_inference.tree.trie_postprocess._detail as detail


def test_base_class():
    assert issubclass(
        hstrat.SampleAncestralRollbacksTriePostprocessor,
        detail.TriePostprocessorBase,
    )


# Test case for a trie with only one node
@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize(
    "p_differentia_collision",
    [
        0,
        0.5,
        1.0,
    ],
)
def test_sample_ancestral_rollbacks_single_node_trie(
    mutate,
    p_differentia_collision,
):
    trie = impl.TrieInnerNode()
    root = hstrat.SampleAncestralRollbacksTriePostprocessor()(
        trie, p_differentia_collision=p_differentia_collision, mutate=mutate
    )
    assert root.parent is None
    # Since there is only one node in the trie, we don't expect any new nodes
    expected_num_nodes = 1
    assert anytree_cardinality(trie) == expected_num_nodes


@pytest.mark.parametrize("mutate", [True, False])
def test_sample_ancestral_rollbacks_multiple_levels_trie_phalf(mutate):
    root = impl.TrieInnerNode(rank=None, differentia=None)
    impl.TrieInnerNode(rank=0, differentia=101, parent=root)
    for i in range(5):
        node = impl.TrieInnerNode(
            rank=1, differentia=i, parent=root.children[0]
        )
        impl.TrieLeafNode(parent=node, taxon_label=f"{i}")
    another = impl.TrieLeafNode(parent=root, taxon_label="another")
    impl.TrieLeafNode(parent=another, taxon_label="another_leaf")

    # (rank None, diff None) @ KQ
    # ├── (rank 0, diff 101) @ MQ
    # │   ├── (rank 1, diff 0) @ NQ
    # │   │   └── 0 @ OQ
    # │   ├── (rank 1, diff 1) @ SQ
    # │   │   └── 1 @ IQ
    # │   ├── (rank 1, diff 2) @ BQ
    # │   │   └── 2 @ CQ
    # │   ├── (rank 1, diff 3) @ HQ
    # │   │   └── 3 @ FQ
    # │   └── (rank 1, diff 4) @ EQ
    # │       └── 4 @ nQ
    # └── another @ jQ
    #     └── another_leaf @ hQ

    original_num_nodes = anytree_cardinality(root)
    original_num_leaves = len(root.leaves)
    assert len(root.children) == 2

    before_ascending_content = [
        [
            (node.taxon_label)
            if isinstance(node, impl.TrieLeafNode)
            else (node._rank, node._differentia)
            for node in AnyTreeAscendingIter(leaf)
        ]
        for leaf in sorted(root.leaves, key=lambda x: x.taxon_label)
    ]

    p_differentia_collision = 0.5
    root = hstrat.SampleAncestralRollbacksTriePostprocessor()(
        root, p_differentia_collision=p_differentia_collision, mutate=mutate
    )
    # for p 0.5, taking into account succession
    # doubles expected unzips from 2 to 4
    assert anytree_cardinality(root) >= original_num_nodes + 4
    assert len(root.leaves) == original_num_leaves
    assert len(root.children) == 6

    assert before_ascending_content == [
        [
            (node.taxon_label)
            if isinstance(node, impl.TrieLeafNode)
            else (node._rank, node._differentia)
            for node in AnyTreeAscendingIter(leaf)
        ]
        for leaf in sorted(root.leaves, key=lambda x: x.taxon_label)
    ]


@pytest.mark.parametrize("mutate", [True, False])
def test_sample_ancestral_rollbacks_multiple_levels_trie_pzero(mutate):
    root = impl.TrieInnerNode(rank=None, differentia=None)
    impl.TrieInnerNode(rank=0, differentia=101, parent=root)
    for i in range(5):
        node = impl.TrieInnerNode(
            rank=1, differentia=i, parent=root.children[0]
        )
        impl.TrieLeafNode(parent=node, taxon_label=f"{i}")
    another = impl.TrieLeafNode(parent=root, taxon_label="another")
    impl.TrieLeafNode(parent=another, taxon_label="another_leaf")

    # (rank None, diff None) @ KQ
    # ├── (rank 0, diff 101) @ MQ
    # │   ├── (rank 1, diff 0) @ NQ
    # │   │   └── 0 @ OQ
    # │   ├── (rank 1, diff 1) @ SQ
    # │   │   └── 1 @ IQ
    # │   ├── (rank 1, diff 2) @ BQ
    # │   │   └── 2 @ CQ
    # │   ├── (rank 1, diff 3) @ HQ
    # │   │   └── 3 @ FQ
    # │   └── (rank 1, diff 4) @ EQ
    # │       └── 4 @ nQ
    # └── another @ jQ
    #     └── another_leaf @ hQ

    original_num_nodes = anytree_cardinality(root)
    original_num_leaves = len(root.leaves)
    assert len(root.children) == 2

    before_ascending_content = [
        [
            (node.taxon_label)
            if isinstance(node, impl.TrieLeafNode)
            else (node._rank, node._differentia)
            for node in AnyTreeAscendingIter(leaf)
        ]
        for leaf in sorted(root.leaves, key=lambda x: x.taxon_label)
    ]

    p_differentia_collision = 0
    root = hstrat.SampleAncestralRollbacksTriePostprocessor()(
        root, p_differentia_collision=p_differentia_collision, mutate=mutate
    )
    assert anytree_cardinality(root) == original_num_nodes
    assert len(root.leaves) == original_num_leaves
    assert len(root.children) == 2

    assert before_ascending_content == [
        [
            (node.taxon_label)
            if isinstance(node, impl.TrieLeafNode)
            else (node._rank, node._differentia)
            for node in AnyTreeAscendingIter(leaf)
        ]
        for leaf in sorted(root.leaves, key=lambda x: x.taxon_label)
    ]


@pytest.mark.parametrize("mutate", [True, False])
def test_sample_ancestral_rollbacks_multiple_levels_trie_pone(mutate):
    root = impl.TrieInnerNode(rank=None, differentia=None)
    impl.TrieInnerNode(rank=0, differentia=101, parent=root)
    for i in range(5):
        node = impl.TrieInnerNode(
            rank=1, differentia=i, parent=root.children[0]
        )
        impl.TrieLeafNode(parent=node, taxon_label=f"{i}")
    another = impl.TrieLeafNode(parent=root, taxon_label="another")
    impl.TrieLeafNode(parent=another, taxon_label="another_leaf")

    # (rank None, diff None) @ KQ
    # ├── (rank 0, diff 101) @ MQ
    # │   ├── (rank 1, diff 0) @ NQ
    # │   │   └── 0 @ OQ
    # │   ├── (rank 1, diff 1) @ SQ
    # │   │   └── 1 @ IQ
    # │   ├── (rank 1, diff 2) @ BQ
    # │   │   └── 2 @ CQ
    # │   ├── (rank 1, diff 3) @ HQ
    # │   │   └── 3 @ FQ
    # │   └── (rank 1, diff 4) @ EQ
    # │       └── 4 @ nQ
    # └── another @ jQ
    #     └── another_leaf @ hQ

    original_num_nodes = anytree_cardinality(root)
    original_num_leaves = len(root.leaves)
    assert len(root.children) == 2

    before_ascending_content = [
        [
            (node.taxon_label)
            if isinstance(node, impl.TrieLeafNode)
            else (node._rank, node._differentia)
            for node in AnyTreeAscendingIter(leaf)
        ]
        for leaf in sorted(root.leaves, key=lambda x: x.taxon_label)
    ]

    p_differentia_collision = 1
    root = hstrat.SampleAncestralRollbacksTriePostprocessor()(
        root, p_differentia_collision=p_differentia_collision, mutate=mutate
    )
    assert anytree_cardinality(root) == original_num_nodes + 4
    assert len(root.leaves) == original_num_leaves
    assert len(root.children) == 6

    assert before_ascending_content == [
        [
            (node.taxon_label)
            if isinstance(node, impl.TrieLeafNode)
            else (node._rank, node._differentia)
            for node in AnyTreeAscendingIter(leaf)
        ]
        for leaf in sorted(root.leaves, key=lambda x: x.taxon_label)
    ]


@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize("tree_size", [10, 30, 100])
@pytest.mark.parametrize(
    "tree_seed",
    range(10),
)
@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.recency_proportional_resolution_algo.Policy(2),
        hstrat.fixed_resolution_algo.Policy(2),
    ],
)
@pytest.mark.parametrize(
    "p_differentia_collision",
    [
        0,
        0.5,
        1.0,
        2**32,  # test full rollback
    ],
)
def test_unzip_fuzz(
    mutate, tree_seed, tree_size, retention_policy, p_differentia_collision
):

    seed_random(tree_seed)
    nx_tree = random_tree(n=tree_size, seed=tree_seed, create_using=nx.DiGraph)
    extant_population = hstrat.descend_template_phylogeny_networkx(
        nx_tree,
        seed_column=hstrat.HereditaryStratigraphicColumn(
            stratum_retention_policy=retention_policy,
        ),
    )
    root = impl.build_trie_from_artifacts(
        extant_population,
        taxon_labels=None,
        progress_wrap=lambda x: x,
    )

    original_num_nodes = anytree_cardinality(root)
    original_num_leaves = len(root.leaves)

    before_ascending_content = [
        [
            (node.taxon_label)
            if isinstance(node, impl.TrieLeafNode)
            else (node._rank, node._differentia)
            for node in AnyTreeAscendingIter(leaf)
        ]
        for leaf in sorted(root.leaves, key=lambda x: x.taxon_label)
    ]

    root = hstrat.SampleAncestralRollbacksTriePostprocessor()(
        root, p_differentia_collision=p_differentia_collision, mutate=mutate
    )
    assert (
        anytree_cardinality(root) > original_num_nodes
        or p_differentia_collision == 0
    )
    assert len(root.leaves) == original_num_leaves
    if p_differentia_collision > 1:
        assert len(root.children) == len(root.leaves)

    assert before_ascending_content == [
        [
            (node.taxon_label)
            if isinstance(node, impl.TrieLeafNode)
            else (node._rank, node._differentia)
            for node in AnyTreeAscendingIter(leaf)
        ]
        for leaf in sorted(root.leaves, key=lambda x: x.taxon_label)
    ]


def test_sample_ancestral_rollbacks_multiple_levels_seed():
    root = impl.TrieInnerNode(rank=None, differentia=None)
    impl.TrieInnerNode(rank=0, differentia=101, parent=root)
    for i in range(5):
        node = impl.TrieInnerNode(
            rank=1, differentia=i, parent=root.children[0]
        )
        impl.TrieLeafNode(parent=node, taxon_label=f"{i}")
    another = impl.TrieLeafNode(parent=root, taxon_label="another")
    impl.TrieLeafNode(parent=another, taxon_label="another_leaf")

    # (rank None, diff None) @ KQ
    # ├── (rank 0, diff 101) @ MQ
    # │   ├── (rank 1, diff 0) @ NQ
    # │   │   └── 0 @ OQ
    # │   ├── (rank 1, diff 1) @ SQ
    # │   │   └── 1 @ IQ
    # │   ├── (rank 1, diff 2) @ BQ
    # │   │   └── 2 @ CQ
    # │   ├── (rank 1, diff 3) @ HQ
    # │   │   └── 3 @ FQ
    # │   └── (rank 1, diff 4) @ EQ
    # │       └── 4 @ nQ
    # └── another @ jQ
    #     └── another_leaf @ hQ

    assert str(
        anytree.RenderTree(
            hstrat.SampleAncestralRollbacksTriePostprocessor(seed=1)(
                root,
                p_differentia_collision=0.5,
                mutate=False,
            )
        ).by_attr("taxon_label")
    ) == str(
        anytree.RenderTree(
            hstrat.SampleAncestralRollbacksTriePostprocessor(seed=1)(
                root,
                p_differentia_collision=0.5,
                mutate=False,
            )
        ).by_attr("taxon_label")
    )

    assert str(
        anytree.RenderTree(
            hstrat.SampleAncestralRollbacksTriePostprocessor(seed=1)(
                root,
                p_differentia_collision=0.5,
                mutate=False,
            )
        ).by_attr("taxon_label")
    ) != str(
        anytree.RenderTree(
            hstrat.SampleAncestralRollbacksTriePostprocessor(seed=3)(
                root,
                p_differentia_collision=0.5,
                mutate=False,
            )
        ).by_attr("taxon_label")
    )


def test_sample_ancestral_rollbacks_multiple_levels_mutate():
    root = impl.TrieInnerNode(rank=None, differentia=None)
    impl.TrieInnerNode(rank=0, differentia=101, parent=root)
    for i in range(5):
        node = impl.TrieInnerNode(
            rank=1, differentia=i, parent=root.children[0]
        )
        impl.TrieLeafNode(parent=node, taxon_label=f"{i}")
    another = impl.TrieLeafNode(parent=root, taxon_label="another")
    impl.TrieLeafNode(parent=another, taxon_label="another_leaf")

    # (rank None, diff None) @ KQ
    # ├── (rank 0, diff 101) @ MQ
    # │   ├── (rank 1, diff 0) @ NQ
    # │   │   └── 0 @ OQ
    # │   ├── (rank 1, diff 1) @ SQ
    # │   │   └── 1 @ IQ
    # │   ├── (rank 1, diff 2) @ BQ
    # │   │   └── 2 @ CQ
    # │   ├── (rank 1, diff 3) @ HQ
    # │   │   └── 3 @ FQ
    # │   └── (rank 1, diff 4) @ EQ
    # │       └── 4 @ nQ
    # └── another @ jQ
    #     └── another_leaf @ hQ

    before = str(anytree.RenderTree(root).by_attr("taxon_label"))
    res = hstrat.SampleAncestralRollbacksTriePostprocessor(seed=1)(
        root,
        p_differentia_collision=0.5,
        mutate=False,
    )
    after = str(anytree.RenderTree(root).by_attr("taxon_label"))

    assert before == after
    assert str(anytree.RenderTree(res).by_attr("taxon_label")) != after
