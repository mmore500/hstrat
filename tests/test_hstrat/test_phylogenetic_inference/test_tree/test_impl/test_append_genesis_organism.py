import pandas as pd

from hstrat._auxiliary_lib import alifestd_make_empty
import hstrat.phylogenetic_inference.tree._impl as impl


def test_append_genesis_organism_empty():
    df = alifestd_make_empty()
    df["origin_time"] = []

    expected_df = pd.DataFrame(
        {
            "id": [0],
            "ancestor_list": ["[none]"],
            "origin_time": [0.0],
        }
    )

    df_ = df.copy()
    extended_df = impl.append_genesis_organism(df)

    assert df.equals(df_)
    assert extended_df.sort_index(axis=1).equals(
        expected_df.sort_index(axis=1)
    )


def test_append_genesis_organism_singleton():
    df = pd.DataFrame(
        {
            "id": [0],
            "ancestor_list": ["[none]"],
            "origin_time": [1],
        }
    )
    expected_df = pd.DataFrame(
        {
            "id": [0, 1],
            "ancestor_list": ["[1]", "[none]"],
            "origin_time": [1, 0],
        }
    )

    df_ = df.copy()
    extended_df = impl.append_genesis_organism(df)

    assert df.equals(df_)
    assert extended_df.equals(expected_df)


def test_append_genesis_organism_one_root():
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_list": ["[1]", "[none]", "[1]", "[2]", "[2]"],
            "origin_time": [8, 1, 2, 1, 11],
            "name": ["A", "B", "C", "D", "E"],
        }
    )
    expected_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5],
            "ancestor_list": ["[1]", "[5]", "[1]", "[2]", "[2]", "[none]"],
            "origin_time": [8, 1, 2, 1, 11, 0],
            "name": ["A", "B", "C", "D", "E", "genesis"],
        }
    )

    df_ = df.copy()
    extended_df = impl.append_genesis_organism(df)

    assert df.equals(df_)
    assert extended_df.equals(expected_df)


def test_append_genesis_organism_two_roots():
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_list": ["[1]", "[none]", "[none]", "[2]", "[2]"],
            "origin_time": [8, 1, 1, 2, 11],
            "name": ["A", "B", "C", "D", "E"],
        }
    )
    expected_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5],
            "ancestor_list": ["[1]", "[5]", "[5]", "[2]", "[2]", "[none]"],
            "origin_time": [8, 1, 1, 2, 11, 0],
            "name": ["A", "B", "C", "D", "E", "genesis"],
        }
    )

    df_ = df.copy()
    extended_df = impl.append_genesis_organism(df)

    assert df.equals(df_)
    assert extended_df.equals(expected_df)


def test_append_genesis_organism_redundant():
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_list": ["[1]", "[none]", "[1]", "[2]", "[2]"],
            "origin_time": [8, 0, 2, 1, 11],
            "name": ["A", "B", "C", "D", "E"],
        }
    )
    expected_df = df.copy()

    df_ = df.copy()
    extended_df = impl.append_genesis_organism(df)

    assert df.equals(df_)
    assert extended_df.equals(expected_df)
