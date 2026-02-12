import os

import pandas as pd
import polars as pl
import pytest

from hstrat._auxiliary_lib import (
    alifestd_assign_contiguous_ids,
    alifestd_find_leaf_ids,
    alifestd_mark_leaves,
    alifestd_topological_sort,
    alifestd_try_add_ancestor_id_col,
)
from hstrat._auxiliary_lib._alifestd_mark_leaves_asexual_polars import (
    alifestd_mark_leaves_asexual_polars,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


def _prepare_polars(phylogeny_df_pd: pd.DataFrame) -> pl.DataFrame:
    """Prepare a pandas phylogeny dataframe for the polars implementation.

    Ensures contiguous ids, topological sort, and ancestor_id column.
    """
    phylogeny_df_pd = alifestd_try_add_ancestor_id_col(phylogeny_df_pd.copy())
    phylogeny_df_pd = alifestd_topological_sort(phylogeny_df_pd)
    phylogeny_df_pd = alifestd_assign_contiguous_ids(phylogeny_df_pd)
    return pl.from_pandas(phylogeny_df_pd)


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
def test_alifestd_mark_leaves_asexual_polars(phylogeny_df):
    """Verify is_leaf column is correctly added."""
    phylogeny_df_pl = _prepare_polars(phylogeny_df)
    result = alifestd_mark_leaves_asexual_polars(phylogeny_df_pl)

    assert "is_leaf" in result.columns
    assert len(result) == len(phylogeny_df_pl)

    # every id in result should match original
    assert result["id"].to_list() == phylogeny_df_pl["id"].to_list()

    # leaves should not appear as ancestor_id of any other node
    internal_ids = set(
        result.filter(pl.col("ancestor_id") != pl.col("id"))
        .select("ancestor_id")
        .to_series()
        .to_list()
    )
    for row in result.iter_rows(named=True):
        if row["is_leaf"]:
            assert row["id"] not in internal_ids
        else:
            assert row["id"] in internal_ids


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
def test_alifestd_mark_leaves_asexual_polars_matches_pandas(phylogeny_df):
    """Verify polars result matches pandas result."""
    phylogeny_df_pd = alifestd_try_add_ancestor_id_col(phylogeny_df.copy())
    phylogeny_df_pd = alifestd_topological_sort(phylogeny_df_pd)
    phylogeny_df_pd = alifestd_assign_contiguous_ids(phylogeny_df_pd)

    phylogeny_df_pl = pl.from_pandas(phylogeny_df_pd)

    result_pd = alifestd_mark_leaves(phylogeny_df_pd, mutate=False)
    result_pl = alifestd_mark_leaves_asexual_polars(phylogeny_df_pl)

    leaf_ids_pd = set(result_pd[result_pd["is_leaf"]]["id"])
    leaf_ids_pl = set(result_pl.filter(pl.col("is_leaf"))["id"].to_list())

    assert leaf_ids_pd == leaf_ids_pl


def test_alifestd_mark_leaves_asexual_polars_empty():
    """Verify empty dataframe gets is_leaf column."""
    phylogeny_df = pl.DataFrame(
        {"id": [], "ancestor_id": []},
        schema={"id": pl.Int64, "ancestor_id": pl.Int64},
    )

    result = alifestd_mark_leaves_asexual_polars(phylogeny_df)

    assert "is_leaf" in result.columns
    assert result.is_empty()


def test_alifestd_mark_leaves_asexual_polars_no_ancestor_id():
    """Verify NotImplementedError for missing ancestor_id."""
    df = pl.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[none]", "[0]", "[1]"],
        }
    )
    with pytest.raises(NotImplementedError):
        alifestd_mark_leaves_asexual_polars(df)


def test_alifestd_mark_leaves_asexual_polars_does_not_mutate():
    """Verify the input dataframe is not mutated."""
    df = pl.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [0, 0, 0, 1],
        }
    )

    original_cols = df.columns[:]
    original_len = len(df)

    _ = alifestd_mark_leaves_asexual_polars(df)

    assert len(df) == original_len
    assert df.columns == original_cols


def test_alifestd_mark_leaves_asexual_polars_simple_chain():
    """Test a simple chain: 0 -> 1 -> 2. Only node 2 is a leaf."""
    df = pl.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_id": [0, 0, 1],
        }
    )

    result = alifestd_mark_leaves_asexual_polars(df)

    leaves = result["is_leaf"].to_list()
    assert leaves == [False, False, True]


def test_alifestd_mark_leaves_asexual_polars_simple_tree():
    """Test a simple tree.

    Tree structure:
        0 (root)
        ├── 1
        │   ├── 3 (leaf)
        │   └── 4 (leaf)
        └── 2 (leaf)
    """
    df = pl.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_id": [0, 0, 0, 1, 1],
        }
    )

    result = alifestd_mark_leaves_asexual_polars(df)

    leaves = result["is_leaf"].to_list()
    assert leaves == [False, False, True, True, True]


def test_alifestd_mark_leaves_asexual_polars_single_node():
    """A single root node with no children is a leaf."""
    df = pl.DataFrame(
        {
            "id": [0],
            "ancestor_id": [0],
        }
    )

    result = alifestd_mark_leaves_asexual_polars(df)

    assert result["is_leaf"].to_list() == [True]


def test_alifestd_mark_leaves_asexual_polars_all_leaves():
    """Multiple roots (all self-referencing) are all leaves."""
    df = pl.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_id": [0, 1, 2],
        }
    )

    result = alifestd_mark_leaves_asexual_polars(df)

    assert result["is_leaf"].to_list() == [True, True, True]


def test_alifestd_mark_leaves_asexual_polars_preserves_columns():
    """Verify original columns are preserved and is_leaf is added."""
    df = pl.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_id": [0, 0, 1],
            "origin_time": [0.0, 1.0, 2.0],
            "taxon_label": ["a", "b", "c"],
        }
    )

    result = alifestd_mark_leaves_asexual_polars(df)

    assert "is_leaf" in result.columns
    assert "origin_time" in result.columns
    assert "taxon_label" in result.columns
    assert result["origin_time"].to_list() == [0.0, 1.0, 2.0]
    assert result["taxon_label"].to_list() == ["a", "b", "c"]
