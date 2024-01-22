import pandas as pd

from hstrat._auxiliary_lib import (
    alifestd_count_root_nodes,
    alifestd_make_empty,
)


def test_empty_df():
    assert alifestd_count_root_nodes(alifestd_make_empty()) == 0


def test_singleton_df():
    df = pd.DataFrame(
        {
            "id": [0],
            "ancestor_list": [[None]],
        }
    )
    assert alifestd_count_root_nodes(df) == 1


def test_sexual_df1():
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_list": ["[None]", "[0]", "[0]", "[1, 0]", "[1]"],
        }
    )
    assert alifestd_count_root_nodes(df) == 1


def test_sexual_df2():
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_list": [[None], [None], [0], [1, 0], [1]],
        }
    )
    assert alifestd_count_root_nodes(df) == 2


def test_polytomy_df():
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_list": [[None], [0], [0], [0], [1]],
        }
    )
    assert alifestd_count_root_nodes(df) == 1


def test_multiple_trees_df1():
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5],
            "ancestor_list": [[None], [None], [0], [2], [2], [3]],
        }
    )
    assert alifestd_count_root_nodes(df) == 2


def test_multiple_trees_df2():
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5],
            "ancestor_list": [[None], [None], [0], [1], [2], [3]],
        }
    )
    assert alifestd_count_root_nodes(df) == 2


def test_multiple_trees_df3():
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_list": [
                "[None]",
                "[None]",
                [0],
                [1],
                [2],
                [3],
                "[None]",
            ],
        }
    )
    assert alifestd_count_root_nodes(df) == 3


def test_multiple_trees_df4():
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_list": [
                "[none]",
                "[none]",
                [0],
                [1],
                [2],
                [3],
                "[none]",
            ],
        }
    )
    assert alifestd_count_root_nodes(df) == 3


def test_strictly_bifurcating_df1():
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_list": [[None], [0], [0], [1], [1]],
        }
    )
    assert alifestd_count_root_nodes(df) == 1


def test_strictly_bifurcating_df2():
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_list": [[], [0], [0], [1], [1]],
        }
    )
    assert alifestd_count_root_nodes(df) == 1


def test_strictly_bifurcating_df3():
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_list": ["[0]", "[0]", "[1]", "[1]", "[None]"],
        }
    )
    assert alifestd_count_root_nodes(df) == 1
