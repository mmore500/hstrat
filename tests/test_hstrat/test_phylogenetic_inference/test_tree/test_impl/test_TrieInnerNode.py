import anytree
import pytest

from hstrat._auxiliary_lib import anytree_cardinality, is_in
import hstrat.phylogenetic_inference.tree._impl as impl


@pytest.fixture
def subtrie():
    # (rank None, diff None) @ B6A
    # └── (rank 0, diff 2) @ BtQ
    #     ├── (rank 3, diff 31) @ jg
    #     └── (rank 3, diff 1) @ BUQ
    #         ├── spice @ 0A
    #         ├── (rank 4, diff 17) @ BxA
    #         │   └── (rank 5, diff 11) @ Gg
    #         │       ├── (rank 6, diff 19) @ Biw
    #         │       └── (rank 6, diff 21) @ HA
    #         │           └── baa @ B-Q
    #         ├── (rank 4, diff 16) @ B7Q
    #         │   └── (rank 5, diff 11) @ sA
    #         │       └── foo @ BtQ
    #         └── (rank 4, diff 17) @ Brw
    #             ├── (rank 6, diff 19) @ BLg
    #             │   └── baz @ B0g
    #             └── (rank 6, diff 19) @ BoA
    #                 └── bar @ B8A

    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    genesis_node = impl.TrieInnerNode(rank=0, differentia=2, parent=root)
    _sibling_node = impl.TrieInnerNode(
        rank=3, differentia=31, parent=genesis_node
    )
    _ = _sibling_node
    focal_node = impl.TrieInnerNode(rank=3, differentia=1, parent=genesis_node)
    impl.TrieLeafNode(focal_node, "spice")
    child1 = impl.TrieInnerNode(rank=4, differentia=17, parent=focal_node)
    child2 = impl.TrieInnerNode(rank=4, differentia=16, parent=focal_node)
    child3 = impl.TrieInnerNode(rank=4, differentia=17, parent=focal_node)
    grandchild1 = impl.TrieInnerNode(rank=5, differentia=11, parent=child1)
    grandchild2 = impl.TrieInnerNode(rank=5, differentia=11, parent=child2)
    impl.TrieLeafNode(grandchild2, "foo")
    greatgrandchild1 = impl.TrieInnerNode(
        rank=6, differentia=19, parent=grandchild1
    )
    greatgrandchild1 = impl.TrieInnerNode(
        rank=6, differentia=21, parent=grandchild1
    )
    impl.TrieLeafNode(greatgrandchild1, "baa")
    greatgrandchild2 = impl.TrieInnerNode(
        rank=6, differentia=19, parent=child3
    )
    impl.TrieLeafNode(greatgrandchild2, "baz")
    greatgrandchild3 = impl.TrieInnerNode(
        rank=6, differentia=19, parent=child3
    )
    impl.TrieLeafNode(greatgrandchild3, "bar")

    return focal_node


def test_is_genesis_of_allele():
    root_node = impl.TrieInnerNode(rank=None, differentia=None)
    inner_node = impl.TrieInnerNode(rank=1, differentia=2, parent=root_node)
    assert inner_node.IsAnOriginationOfAllele(1, 2)
    assert not inner_node.IsAnOriginationOfAllele(1, 3)
    assert not inner_node.IsAnOriginationOfAllele(2, 2)

    assert not root_node.IsAnOriginationOfAllele(1, 2)


def test_find_geneses_of_allele_self(subtrie):
    geneses = [*subtrie.FindOriginationsOfAllele(3, 1)]
    assert len(geneses) == 1
    assert geneses[0] is subtrie


def test_find_geneses_of_allele_singleton(subtrie):
    geneses = [*subtrie.FindOriginationsOfAllele(6, 21)]
    assert len(geneses) == 1
    assert geneses[0].IsAnOriginationOfAllele(6, 21)


def test_find_geneses_of_allele_multiple(subtrie):
    geneses = [*subtrie.FindOriginationsOfAllele(6, 19)]
    assert len(geneses) == 3

    for genesis in geneses:
        assert genesis.IsAnOriginationOfAllele(6, 19)

    geneses = [*subtrie.FindOriginationsOfAllele(4, 17)]
    assert len(geneses) == 2

    for genesis in geneses:
        assert genesis.IsAnOriginationOfAllele(4, 17)

    geneses = [*subtrie.FindOriginationsOfAllele(5, 11)]
    assert len(geneses) == 2

    for genesis in geneses:
        assert genesis.IsAnOriginationOfAllele(5, 11)


def test_find_geneses_of_allele_failure(subtrie):
    geneses = [*subtrie.FindOriginationsOfAllele(3, 19)]
    assert len(geneses) == 0

    geneses = [*subtrie.FindOriginationsOfAllele(3, 31)]
    assert len(geneses) == 0

    geneses = [*subtrie.FindOriginationsOfAllele(11, 31)]
    assert len(geneses) == 0

    geneses = [*subtrie.FindOriginationsOfAllele(5, 21)]
    assert len(geneses) == 0


def test_get_deepest_consecutive_shared_allele_genesis_with_empty_iterator(
    subtrie,
):
    (
        genesis,
        leftover_iter,
    ) = subtrie.GetDeepestCongruousAlleleOrigination(iter([]))
    assert genesis is subtrie
    assert [*leftover_iter] == []


def test_get_deepest_consecutive_shared_allele_genesis_singleton(
    subtrie,
):
    # test with a non-empty iterator
    alleles = [(4, 16), (5, 11)]
    (
        genesis,
        leftover_iter,
    ) = subtrie.GetDeepestCongruousAlleleOrigination(iter(alleles))
    assert genesis.IsAnOriginationOfAllele(5, 11)
    assert genesis.parent.IsAnOriginationOfAllele(4, 16)
    assert [*leftover_iter] == []

    alleles = [(4, 16)]
    (
        genesis,
        leftover_iter,
    ) = subtrie.GetDeepestCongruousAlleleOrigination(iter(alleles))
    assert genesis.IsAnOriginationOfAllele(4, 16)
    assert [*leftover_iter] == []

    alleles = [(4, 16), (5, 11), (7, 28), (8, 19)]
    (
        genesis,
        leftover_iter,
    ) = subtrie.GetDeepestCongruousAlleleOrigination(iter(alleles))
    assert genesis.IsAnOriginationOfAllele(5, 11)
    assert genesis.parent.IsAnOriginationOfAllele(4, 16)
    assert [*leftover_iter] == alleles[2:]

    alleles = [(4, 16), (6, 19)]
    (
        genesis,
        leftover_iter,
    ) = subtrie.GetDeepestCongruousAlleleOrigination(iter(alleles))
    assert genesis.IsAnOriginationOfAllele(4, 16)
    assert [*leftover_iter] == alleles[1:]


def test_get_deepest_consecutive_shared_allele_genesis_tiebreaker(
    subtrie,
):
    # test with a non-empty iterator
    alleles = [(4, 17), (6, 19), (7, 22)]
    (
        genesis,
        leftover_iter,
    ) = subtrie.GetDeepestCongruousAlleleOrigination(iter(alleles))
    assert genesis.IsAnOriginationOfAllele(6, 19)
    assert [*leftover_iter] == alleles[2:]

    (
        genesis2,
        leftover_iter,
    ) = subtrie.GetDeepestCongruousAlleleOrigination(iter(alleles))
    assert genesis2 is genesis
    assert [*leftover_iter] == alleles[2:]

    alleles = [(4, 17)]
    (
        genesis,
        leftover_iter,
    ) = subtrie.GetDeepestCongruousAlleleOrigination(iter(alleles))
    assert is_in(genesis2, anytree.PostOrderIter(genesis))
    assert [*leftover_iter] == []


def test_insert_taxon_canopy1(subtrie):
    previous_node_count = anytree_cardinality(subtrie)
    alleles = [(4, 17)]
    (
        genesis,
        leftover_iter,
    ) = subtrie.GetDeepestCongruousAlleleOrigination(iter(alleles))
    assert [*leftover_iter] == []

    inserted = genesis.InsertTaxon("fab", iter([]))
    assert inserted.taxon == "fab"
    assert inserted.parent is genesis
    assert inserted.parent.IsAnOriginationOfAllele(4, 17)
    assert anytree_cardinality(subtrie) == previous_node_count + 1
    previous_node_count = anytree_cardinality(subtrie)

    inserted = genesis.InsertTaxon("far", iter([(9, 12)]))
    assert inserted.taxon == "far"
    assert inserted.parent.parent is genesis
    assert inserted.parent.IsAnOriginationOfAllele(9, 12)
    assert anytree_cardinality(subtrie) == previous_node_count + 2
    previous_node_count = anytree_cardinality(subtrie)


def test_insert_taxon_canopy2(subtrie):
    previous_node_count = anytree_cardinality(subtrie)
    alleles = [(4, 17), (6, 19)]
    (
        genesis,
        leftover_iter,
    ) = subtrie.GetDeepestCongruousAlleleOrigination(iter(alleles))
    assert [*leftover_iter] == []
    inserted = genesis.InsertTaxon("fab", iter([]))
    assert inserted.taxon == "fab"
    assert inserted.parent is genesis
    assert anytree_cardinality(subtrie) == previous_node_count + 1
    previous_node_count = anytree_cardinality(subtrie)

    inserted = genesis.InsertTaxon("far", iter([(7, 12)]))
    assert inserted.taxon == "far"
    assert inserted.parent.parent is genesis
    assert anytree_cardinality(subtrie) == previous_node_count + 2


def test_insert_taxon_canopy3(subtrie):
    previous_node_count = anytree_cardinality(subtrie)
    alleles = [(4, 17), (6, 19)]
    (
        genesis,
        leftover_iter,
    ) = subtrie.GetDeepestCongruousAlleleOrigination(iter(alleles))
    assert [*leftover_iter] == []

    inserted = genesis.InsertTaxon("gg", iter([(7, 12), (8, 20)]))
    assert inserted.taxon == "gg"
    assert inserted.parent.parent.parent is genesis
    assert inserted.parent.IsAnOriginationOfAllele(8, 20)
    assert inserted.parent.parent.IsAnOriginationOfAllele(7, 12)
    assert anytree_cardinality(subtrie) == previous_node_count + 3


def test_insert_taxon_internal1(subtrie):
    previous_node_count = anytree_cardinality(subtrie)
    alleles = [(4, 17)]
    (
        genesis,
        leftover_iter,
    ) = subtrie.GetDeepestCongruousAlleleOrigination(iter(alleles))
    assert [*leftover_iter] == []
    children_before = [*genesis.children]

    inserted = genesis.InsertTaxon("fab", iter([(5, 11)]))
    assert inserted.taxon_label == "fab"
    assert inserted.parent.IsAnOriginationOfAllele(5, 11)
    assert is_in(inserted.parent, children_before)
    assert inserted.parent.parent is genesis
    assert anytree_cardinality(subtrie) == previous_node_count + 1


def test_insert_taxon_internal2(subtrie):
    previous_node_count = anytree_cardinality(subtrie)
    alleles = [(4, 17)]
    (
        genesis,
        leftover_iter,
    ) = subtrie.GetDeepestCongruousAlleleOrigination(iter(alleles))
    assert [*leftover_iter] == []
    descendants_before = [*anytree.PostOrderIter(genesis)]

    inserted = genesis.InsertTaxon("fab", iter([(5, 11), (6, 21)]))
    assert inserted.taxon_label == "fab"
    assert inserted.parent.IsAnOriginationOfAllele(6, 21)
    assert anytree_cardinality(subtrie) == previous_node_count + 1

    previous_node_count = anytree_cardinality(subtrie)
    descendants_before = [*anytree.PostOrderIter(genesis)]
    inserted = genesis.InsertTaxon("fan", iter([(5, 11), (6, 21)]))
    assert inserted.taxon_label == "fan"
    assert is_in(inserted.parent, descendants_before)
    assert anytree_cardinality(subtrie) == previous_node_count + 1


def test_insert_taxon_internal3(subtrie):
    alleles = [(4, 17)]
    (
        genesis,
        leftover_iter,
    ) = subtrie.GetDeepestCongruousAlleleOrigination(iter(alleles))
    assert [*leftover_iter] == []
    inserted = genesis.InsertTaxon("fab", iter([(5, 11), (6, 21)]))
    assert inserted.taxon_label == "fab"
    previous_node_count = anytree_cardinality(subtrie)
    descendants_before = [*anytree.PostOrderIter(genesis)]

    inserted = genesis.InsertTaxon(
        "bat", iter([(5, 11), (6, 21), (10, 10), (11, 19)])
    )
    assert inserted.taxon_label == "bat"
    assert inserted.parent.IsAnOriginationOfAllele(11, 19)
    assert inserted.parent.parent.IsAnOriginationOfAllele(10, 10)
    assert inserted.parent.parent.parent.IsAnOriginationOfAllele(6, 21)
    assert not is_in(inserted.parent, descendants_before)
    assert not is_in(inserted.parent.parent, descendants_before)
    assert is_in(inserted.parent.parent.parent, descendants_before)
    assert anytree_cardinality(subtrie) == previous_node_count + 3


def test_taxon_and_taxon_label(subtrie):
    taxon_labels = [
        node.taxon_label for node in anytree.PostOrderIter(subtrie)
    ]
    assert len(taxon_labels) == len(set(taxon_labels))

    for node in anytree.PostOrderIter(subtrie):
        assert node.taxon == node.taxon_label
        assert isinstance(node.taxon, str)


def test_inner_children(subtrie):
    assert len([*subtrie.inner_children]) == 3
    assert len(set(map(id, subtrie.inner_children))) == 3
    assert all(
        isinstance(node, impl.TrieInnerNode) for node in subtrie.inner_children
    )
    assert all(node.parent is subtrie for node in subtrie.inner_children)


def test_outer_children(subtrie):
    assert len([*subtrie.outer_children]) == 1
    assert len(set(map(id, subtrie.outer_children))) == 1
    assert all(
        isinstance(node, impl.TrieLeafNode) for node in subtrie.outer_children
    )
    assert all(node.parent is subtrie for node in subtrie.outer_children)
