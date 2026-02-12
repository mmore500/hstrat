import os
import typing

import pandas as pd
import polars as pl
import pytest

from hstrat._auxiliary_lib import (
    alifestd_assign_contiguous_ids,
    alifestd_mark_leaves,
    alifestd_topological_sort,
    alifestd_try_add_ancestor_id_col,
)
from hstrat._auxiliary_lib._alifestd_mark_leaves_polars import (
    alifestd_mark_leaves_polars,
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
@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_mark_leaves_polars_fuzz(
    phylogeny_df: pd.DataFrame, apply: typing.Callable
):
    """Verify is_leaf column is correctly added."""
    df_prepared = _prepare_polars(phylogeny_df)
    df_pl = apply(df_prepared)

    result = alifestd_mark_leaves_polars(df_pl).lazy().collect()

    assert "is_leaf" in result.columns
    assert len(result) == len(df_prepared)

    # every id in result should match original
    assert result["id"].to_list() == df_prepared["id"].to_list()

    # leaves should not appear as ancestor_id of any other non-root node
    internal_ids = set(
        df_prepared.filter(pl.col("ancestor_id") != pl.col("id"))
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
@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_mark_leaves_polars_matches_pandas(
    phylogeny_df: pd.DataFrame, apply: typing.Callable
):
    """Verify polars result matches pandas result."""
    phylogeny_df_pd = alifestd_try_add_ancestor_id_col(phylogeny_df.copy())
    phylogeny_df_pd = alifestd_topological_sort(phylogeny_df_pd)
    phylogeny_df_pd = alifestd_assign_contiguous_ids(phylogeny_df_pd)

    result_pd = alifestd_mark_leaves(phylogeny_df_pd, mutate=False)

    df_pl = apply(pl.from_pandas(phylogeny_df_pd))
    result_pl = alifestd_mark_leaves_polars(df_pl).lazy().collect()

    leaf_ids_pd = set(result_pd[result_pd["is_leaf"]]["id"])
    leaf_ids_pl = set(
        result_pl.filter(pl.col("is_leaf"))["id"].to_list(),
    )
    assert leaf_ids_pd == leaf_ids_pl


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_mark_leaves_polars_simple_chain(apply: typing.Callable):
    """Test a simple chain: 0 -> 1 -> 2. Only node 2 is a leaf."""
    df_pl = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_id": [0, 0, 1],
            }
        ),
    )

    result = alifestd_mark_leaves_polars(df_pl).lazy().collect()

    assert result["is_leaf"].to_list() == [False, False, True]


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_mark_leaves_polars_simple_tree(apply: typing.Callable):
    """Test a simple tree.

    Tree structure:
        0 (root)
        +-- 1
        |   +-- 3 (leaf)
        |   +-- 4 (leaf)
        +-- 2 (leaf)
    """
    df_pl = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2, 3, 4],
                "ancestor_id": [0, 0, 0, 1, 1],
            }
        ),
    )

    result = alifestd_mark_leaves_polars(df_pl).lazy().collect()

    assert result["is_leaf"].to_list() == [False, False, True, True, True]


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_mark_leaves_polars_two_roots(apply: typing.Callable):
    """Two independent roots with children."""
    df_pl = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2, 3],
                "ancestor_id": [0, 1, 0, 1],
            }
        ),
    )

    result = alifestd_mark_leaves_polars(df_pl).lazy().collect()

    assert result["is_leaf"].to_list() == [False, False, True, True]


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_mark_leaves_polars_all_leaves(apply: typing.Callable):
    """Multiple roots (all self-referencing) are all leaves."""
    df_pl = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_id": [0, 1, 2],
            }
        ),
    )

    result = alifestd_mark_leaves_polars(df_pl).lazy().collect()

    assert result["is_leaf"].to_list() == [True, True, True]


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_mark_leaves_polars_single_node(apply: typing.Callable):
    """A single root node with no children is a leaf."""
    df_pl = apply(
        pl.DataFrame(
            {
                "id": [0],
                "ancestor_id": [0],
            }
        ),
    )

    result = alifestd_mark_leaves_polars(df_pl).lazy().collect()

    assert result["is_leaf"].to_list() == [True]


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_mark_leaves_polars_empty(apply: typing.Callable):
    """Empty dataframe gets is_leaf column."""
    df_pl = apply(
        pl.DataFrame(
            {"id": [], "ancestor_id": []},
            schema={"id": pl.Int64, "ancestor_id": pl.Int64},
        ),
    )

    result = alifestd_mark_leaves_polars(df_pl).lazy().collect()

    assert "is_leaf" in result.columns
    assert result.is_empty()


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_mark_leaves_polars_preserves_columns(apply: typing.Callable):
    """Verify original columns are preserved and is_leaf is added."""
    df_pl = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_id": [0, 0, 1],
                "origin_time": [0.0, 1.0, 2.0],
                "taxon_label": ["a", "b", "c"],
            }
        ),
    )

    result = alifestd_mark_leaves_polars(df_pl).lazy().collect()

    assert "is_leaf" in result.columns
    assert "origin_time" in result.columns
    assert "taxon_label" in result.columns
    assert result["origin_time"].to_list() == [0.0, 1.0, 2.0]
    assert result["taxon_label"].to_list() == ["a", "b", "c"]


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_mark_leaves_polars_does_not_mutate(apply: typing.Callable):
    """Verify the input dataframe is not mutated."""
    df_eager = pl.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [0, 0, 0, 1],
        }
    )
    df_pl = apply(df_eager)

    original_cols = df_eager.columns[:]
    original_len = len(df_eager)

    _ = alifestd_mark_leaves_polars(df_pl).lazy().collect()

    assert len(df_eager) == original_len
    assert df_eager.columns == original_cols


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_mark_leaves_polars_with_preexisting_num_children(
    apply: typing.Callable,
):
    """If num_children already exists, it should be used directly."""
    df_pl = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_id": [0, 0, 1],
                "num_children": [1, 1, 0],
            }
        ),
    )

    result = alifestd_mark_leaves_polars(df_pl).lazy().collect()

    assert result["is_leaf"].to_list() == [False, False, True]
