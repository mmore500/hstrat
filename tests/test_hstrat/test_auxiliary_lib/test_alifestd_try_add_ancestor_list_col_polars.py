import os

import pandas as pd
import polars as pl
import pytest

from hstrat._auxiliary_lib import (
    alifestd_try_add_ancestor_id_col,
    alifestd_try_add_ancestor_list_col,
)
from hstrat._auxiliary_lib._alifestd_make_ancestor_list_col_polars import (
    alifestd_make_ancestor_list_col_polars,
)
from hstrat._auxiliary_lib._alifestd_try_add_ancestor_list_col_polars import (
    alifestd_try_add_ancestor_list_col_polars,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(
            f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
        ),
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
def test_alifestd_try_add_ancestor_list_col_polars_adds_col(phylogeny_df):
    """Verify ancestor_list is added when ancestor_id is present."""
    phylogeny_df_pd = alifestd_try_add_ancestor_id_col(phylogeny_df.copy())
    df = pl.from_pandas(phylogeny_df_pd[["id", "ancestor_id"]])

    assert "ancestor_list" not in df.columns
    result = alifestd_try_add_ancestor_list_col_polars(df)

    assert "ancestor_list" in result.columns
    assert len(result) == len(df)


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(
            f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
        ),
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
def test_alifestd_try_add_ancestor_list_col_polars_correctness(phylogeny_df):
    """Verify generated ancestor_list matches expected values."""
    phylogeny_df_pd = alifestd_try_add_ancestor_id_col(phylogeny_df.copy())
    df = pl.from_pandas(phylogeny_df_pd[["id", "ancestor_id"]])

    result = alifestd_try_add_ancestor_list_col_polars(df)

    expected = alifestd_make_ancestor_list_col_polars(
        result["id"],
        result["ancestor_id"],
        root_ancestor_token="none",
    )
    assert result["ancestor_list"].to_list() == expected.to_list()


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(
            f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
        ),
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
def test_alifestd_try_add_ancestor_list_col_polars_matches_pandas(
    phylogeny_df,
):
    """Verify polars result matches pandas result."""
    phylogeny_df_pd = alifestd_try_add_ancestor_id_col(phylogeny_df.copy())

    # Run pandas version (drop ancestor_list first to force re-creation)
    pd_input = phylogeny_df_pd.drop(columns="ancestor_list")
    result_pd = alifestd_try_add_ancestor_list_col(pd_input)

    # Run polars version
    pl_input = pl.from_pandas(pd_input)
    result_pl = alifestd_try_add_ancestor_list_col_polars(pl_input)

    assert result_pd["ancestor_list"].tolist() == (
        result_pl["ancestor_list"].to_list()
    )


def test_alifestd_try_add_ancestor_list_col_polars_already_has_col():
    """Verify no change when ancestor_list column already exists."""
    df = pl.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_id": [0, 0, 1],
            "ancestor_list": ["[none]", "[0]", "[1]"],
        }
    )

    result = alifestd_try_add_ancestor_list_col_polars(df)

    assert result["ancestor_list"].to_list() == ["[none]", "[0]", "[1]"]
    assert result.equals(df)


def test_alifestd_try_add_ancestor_list_col_polars_no_ancestor_id():
    """Verify no change when ancestor_id column is missing."""
    df = pl.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[none]", "[0]", "[1]"],
        }
    )

    result = alifestd_try_add_ancestor_list_col_polars(df)

    assert result.equals(df)


def test_alifestd_try_add_ancestor_list_col_polars_neither_col():
    """Verify no change when both ancestor_id and ancestor_list are missing."""
    df = pl.DataFrame(
        {
            "id": [0, 1, 2],
            "origin_time": [0.0, 1.0, 2.0],
        }
    )

    result = alifestd_try_add_ancestor_list_col_polars(df)

    assert "ancestor_list" not in result.columns
    assert result.equals(df)


def test_alifestd_try_add_ancestor_list_col_polars_simple_chain():
    """Test a simple chain: 0 -> 1 -> 2."""
    df = pl.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_id": [0, 0, 1],
        }
    )

    result = alifestd_try_add_ancestor_list_col_polars(df)

    assert "ancestor_list" in result.columns
    assert result["ancestor_list"].to_list() == ["[none]", "[0]", "[1]"]


def test_alifestd_try_add_ancestor_list_col_polars_simple_tree():
    """Test a simple tree.

    Tree structure:
        0 (root)
        +-- 1
        |   +-- 3
        |   +-- 4
        +-- 2
    """
    df = pl.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_id": [0, 0, 0, 1, 1],
        }
    )

    result = alifestd_try_add_ancestor_list_col_polars(df)

    assert result["ancestor_list"].to_list() == [
        "[none]",
        "[0]",
        "[0]",
        "[1]",
        "[1]",
    ]


def test_alifestd_try_add_ancestor_list_col_polars_root_ancestor_token():
    """Test custom root_ancestor_token."""
    df = pl.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_id": [0, 0, 1],
        }
    )

    result = alifestd_try_add_ancestor_list_col_polars(
        df, root_ancestor_token="None"
    )
    assert result["ancestor_list"].to_list() == ["[None]", "[0]", "[1]"]

    result2 = alifestd_try_add_ancestor_list_col_polars(
        df, root_ancestor_token=""
    )
    assert result2["ancestor_list"].to_list() == ["[]", "[0]", "[1]"]


def test_alifestd_try_add_ancestor_list_col_polars_single_node():
    """A single root node."""
    df = pl.DataFrame(
        {
            "id": [0],
            "ancestor_id": [0],
        }
    )

    result = alifestd_try_add_ancestor_list_col_polars(df)

    assert result["ancestor_list"].to_list() == ["[none]"]


def test_alifestd_try_add_ancestor_list_col_polars_empty():
    """Verify empty dataframe."""
    df = pl.DataFrame(
        {"id": [], "ancestor_id": []},
        schema={"id": pl.Int64, "ancestor_id": pl.Int64},
    )

    result = alifestd_try_add_ancestor_list_col_polars(df)

    assert "ancestor_list" in result.columns
    assert result.is_empty()


def test_alifestd_try_add_ancestor_list_col_polars_preserves_columns():
    """Verify original columns are preserved."""
    df = pl.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_id": [0, 0, 1],
            "origin_time": [0.0, 1.0, 2.0],
            "taxon_label": ["a", "b", "c"],
        }
    )

    result = alifestd_try_add_ancestor_list_col_polars(df)

    assert "ancestor_list" in result.columns
    assert "origin_time" in result.columns
    assert "taxon_label" in result.columns
    assert result["origin_time"].to_list() == [0.0, 1.0, 2.0]
    assert result["taxon_label"].to_list() == ["a", "b", "c"]


def test_alifestd_try_add_ancestor_list_col_polars_idempotent():
    """Calling twice should produce the same result."""
    df = pl.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_id": [0, 0, 1],
        }
    )

    result1 = alifestd_try_add_ancestor_list_col_polars(df)
    result2 = alifestd_try_add_ancestor_list_col_polars(result1)

    assert (
        result1["ancestor_list"].to_list()
        == result2["ancestor_list"].to_list()
    )


def test_alifestd_try_add_ancestor_list_col_polars_does_not_mutate():
    """Verify the input dataframe is not mutated."""
    df = pl.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_id": [0, 0, 1],
        }
    )

    original_cols = df.columns[:]
    original_len = len(df)

    _ = alifestd_try_add_ancestor_list_col_polars(df)

    assert len(df) == original_len
    assert df.columns == original_cols


def test_alifestd_try_add_ancestor_list_col_polars_two_roots():
    """Two independent root nodes."""
    df = pl.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [0, 1, 0, 1],
        }
    )

    result = alifestd_try_add_ancestor_list_col_polars(df)

    assert result["ancestor_list"].to_list() == [
        "[none]",
        "[none]",
        "[0]",
        "[1]",
    ]
