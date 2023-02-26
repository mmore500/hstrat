import anytree

from hstrat.phylogenetic_inference.tree._impl import _TrieNode as impl


def test_GetDescendants():
    root = impl.TrieInnerNode()
    commonancestor = impl.TrieInnerNode(rank=0, differentia=0, parent=root)

    zipto = impl.TrieInnerNode(rank=5, differentia=3, parent=commonancestor)
    zipto_child = impl.TrieInnerNode(rank=7, differentia=9, parent=zipto)
    midpoint = impl.TrieInnerNode(rank=2, differentia=7, parent=commonancestor)
    zipfrom = impl.TrieInnerNode(rank=5, differentia=3, parent=midpoint)

    assert [zipfrom] == [*midpoint.GetDescendants(rank=5, differentia=3)]


def test_Rezip_simple():
    root = impl.TrieInnerNode()
    commonancestor = impl.TrieInnerNode(rank=0, differentia=0, parent=root)

    zipto = impl.TrieInnerNode(rank=5, differentia=3, parent=commonancestor)
    zipto_child = impl.TrieInnerNode(rank=7, differentia=9, parent=zipto)
    midpoint = impl.TrieInnerNode(rank=2, differentia=7, parent=commonancestor)
    zipfrom = impl.TrieInnerNode(rank=5, differentia=3, parent=midpoint)

    commonancestor.Rezip()
    assert zipto.parent is None
    assert zipfrom.parent is midpoint
    assert zipto_child.parent is zipfrom
    assert midpoint.parent is commonancestor
    assert commonancestor.parent is root
    assert root.parent is None


def test_Rezip_competition():
    root = impl.TrieInnerNode()
    commonancestor = impl.TrieInnerNode(rank=0, differentia=0, parent=root)

    zipto = impl.TrieInnerNode(rank=5, differentia=3, parent=commonancestor)
    zipto_child = impl.TrieInnerNode(rank=7, differentia=9, parent=zipto)
    midpoint = impl.TrieInnerNode(rank=2, differentia=7, parent=commonancestor)
    zipfrom = impl.TrieInnerNode(rank=5, differentia=3, parent=midpoint)
    zipfrom_child1 = impl.TrieInnerNode(rank=7, differentia=9, parent=zipto)
    midpoint_loser = impl.TrieInnerNode(
        rank=2, differentia=9, parent=commonancestor
    )
    zipfrom_loser = impl.TrieInnerNode(
        rank=5, differentia=3, parent=midpoint_loser
    )

    commonancestor.Rezip()

    assert zipto.parent is None
    assert zipfrom.parent is midpoint
    assert zipto_child.parent is zipfrom
    assert midpoint.parent is commonancestor
    assert commonancestor.parent is root
    assert root.parent is None

    assert midpoint_loser.parent is commonancestor
    assert zipfrom_loser.parent is midpoint_loser


def test_Rezip_consecutive():
    root = impl.TrieInnerNode()
    commonancestor = impl.TrieInnerNode(rank=0, differentia=0, parent=root)

    zipto = impl.TrieInnerNode(rank=5, differentia=3, parent=commonancestor)
    zipto_child = impl.TrieInnerNode(rank=7, differentia=9, parent=zipto)
    midpoint = impl.TrieInnerNode(rank=2, differentia=7, parent=commonancestor)
    zipfrom = impl.TrieInnerNode(rank=5, differentia=3, parent=midpoint)
    zipfrom_child1 = impl.TrieInnerNode(rank=7, differentia=9, parent=zipfrom)
    midpoint_loser = impl.TrieInnerNode(
        rank=2, differentia=9, parent=commonancestor
    )
    zipfrom_loser = impl.TrieInnerNode(
        rank=5, differentia=3, parent=midpoint_loser
    )

    print("go")
    print(anytree.RenderTree(root))
    for node in [*anytree.PreOrderIter(root)]:
        if isinstance(node, impl.TrieInnerNode):
            print(node)
            print(anytree.RenderTree(root))
            node.Rezip()

    assert zipto.parent is None
    assert zipfrom.parent is midpoint
    assert midpoint.parent is commonancestor
    assert commonancestor.parent is root
    assert root.parent is None

    assert midpoint_loser.parent is commonancestor
    assert zipfrom_loser.parent is midpoint_loser

    assert {zipto_child.parent, zipfrom_child1.parent} == {None, zipfrom}
