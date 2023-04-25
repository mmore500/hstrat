import networkx as nx
import pytest

from hstrat import hstrat


def test_empty():
    tree = nx.DiGraph()
    assert (
        hstrat.descend_template_phylogeny_networkx(
            tree, hstrat.HereditaryStratigraphicColumn()
        )
        == []
    )


def test_singleton():
    tree = nx.DiGraph()
    tree.add_nodes_from([0])

    ancestor = hstrat.HereditaryStratigraphicColumn().CloneNthDescendant(19)
    assert hstrat.descend_template_phylogeny_networkx(tree, ancestor) == [
        ancestor
    ]


def test_tree():
    tree = nx.DiGraph()
    tree.add_edges_from([(0, 1), (1, 2), (1, 3), (3, 4)])
    seed_column = hstrat.HereditaryStratigraphicColumn().CloneNthDescendant(1)
    result = hstrat.descend_template_phylogeny_networkx(tree, seed_column)
    assert len(result) == 2
    assert [*tree.nodes].index(2) < [*tree.nodes].index(4)

    col2, col4 = result

    assert col2.GetNumStrataDeposited() == 4
    assert col4.GetNumStrataDeposited() == 5
    assert (
        hstrat.estimate_patristic_distance_between(
            col2, col4, "maximum_likelihood", "arbitrary"
        )
        == 3
    )


def test_forest():
    tree = nx.DiGraph()
    tree.add_edges_from([(0, 1), (0, 2), (2, 3)])
    tree.add_edges_from([(4, 5), (4, 6), (6, 7)])
    with pytest.raises(ValueError):
        hstrat.descend_template_phylogeny_networkx(
            tree, hstrat.HereditaryStratigraphicColumn()
        )


def test_tree_internal_extant_nodes():
    tree = nx.DiGraph()
    tree.add_edges_from([(0, 1), (1, 2), (1, 3), (3, 4)])
    seed_column = hstrat.HereditaryStratigraphicColumn().CloneNthDescendant(1)
    result = hstrat.descend_template_phylogeny_networkx(
        tree, seed_column, extant_nodes=[2, 3, 4]
    )
    assert len(result) == 3

    col2, col3, col4 = result

    assert col2.GetNumStrataDeposited() == 4
    assert col3.GetNumStrataDeposited() == 4
    assert col4.GetNumStrataDeposited() == 5
    assert (
        hstrat.estimate_patristic_distance_between(
            col2, col4, "maximum_likelihood", "arbitrary"
        )
        == 3
    )
    assert (
        hstrat.estimate_patristic_distance_between(
            col3, col4, "maximum_likelihood", "arbitrary"
        )
        == 1
    )
    assert (
        hstrat.estimate_patristic_distance_between(
            col2, col3, "maximum_likelihood", "arbitrary"
        )
        == 2
    )
