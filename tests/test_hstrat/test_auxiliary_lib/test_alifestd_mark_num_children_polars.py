import os

import pandas as pd
import polars as pl
import pytest

from hstrat._auxiliary_lib import (
    alifestd_assign_contiguous_ids,
    alifestd_mark_num_children_asexual,
    alifestd_topological_sort,
    alifestd_try_add_ancestor_id_col,
)
from hstrat._auxiliary_lib._alifestd_mark_num_children_polars import (
    alifestd_mark_num_children_polars,
)

pytestmark = pytest.mark.filterwarnings(
    "ignore::polars.exceptions.PerformanceWarning"
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.fixture(
    params=[
        pytest.param(False, id="DataFrame"),
        pytest.param(True, id="LazyFrame"),
    ]
)
def lazy(request):
    return request.param


def _apply_lazy(df: pl.DataFrame, lazy: bool):
    """Return DataFrame or LazyFrame depending on fixture."""
    if lazy:
        return df.lazy()
    return df


def _collect(result):
    """Collect LazyFrame to DataFrame for assertions."""
    if isinstance(result, pl.LazyFrame):
        return result.collect()
    return result


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
def test_alifestd_mark_num_children_polars_fuzz(phylogeny_df, lazy):
    """Verify num_children column is correctly added."""
    df_prepared = _prepare_polars(phylogeny_df)
    df_pl = _apply_lazy(df_prepared, lazy)

    result = _collect(alifestd_mark_num_children_polars(df_pl))

    assert "num_children" in result.columns
    assert len(result) == len(df_prepared)

    # every id in result should match original
    assert result["id"].to_list() == df_prepared["id"].to_list()

    # all counts should be non-negative
    assert (result["num_children"] >= 0).all()

    # all counts should be less than total number of nodes
    assert (result["num_children"] < len(result)).all()

    # leaves (not appearing as ancestor of any non-root node) should have 0
    internal_ids = set(
        df_prepared.filter(pl.col("ancestor_id") != pl.col("id"))
        .select("ancestor_id")
        .to_series()
        .to_list()
    )
    for row in result.iter_rows(named=True):
        if row["id"] not in internal_ids:
            assert row["num_children"] == 0
        else:
            assert row["num_children"] >= 1


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
def test_alifestd_mark_num_children_polars_matches_pandas(phylogeny_df, lazy):
    """Verify polars result matches pandas result."""
    phylogeny_df_pd = alifestd_try_add_ancestor_id_col(phylogeny_df.copy())
    phylogeny_df_pd = alifestd_topological_sort(phylogeny_df_pd)
    phylogeny_df_pd = alifestd_assign_contiguous_ids(phylogeny_df_pd)

    result_pd = alifestd_mark_num_children_asexual(
        phylogeny_df_pd, mutate=False
    )

    df_pl = _apply_lazy(pl.from_pandas(phylogeny_df_pd), lazy)
    result_pl = _collect(alifestd_mark_num_children_polars(df_pl))

    assert result_pd["num_children"].tolist() == (
        result_pl["num_children"].to_list()
    )


def test_alifestd_mark_num_children_polars_simple_chain(lazy):
    """Test a simple chain: 0 -> 1 -> 2."""
    df_pl = _apply_lazy(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_id": [0, 0, 1],
            }
        ),
        lazy,
    )

    result = _collect(alifestd_mark_num_children_polars(df_pl))

    assert result["num_children"].to_list() == [1, 1, 0]


def test_alifestd_mark_num_children_polars_simple_tree(lazy):
    """Test a simple tree.

    Tree structure:
        0 (root)
        +-- 1
        |   +-- 3
        |   +-- 4
        +-- 2
    """
    df_pl = _apply_lazy(
        pl.DataFrame(
            {
                "id": [0, 1, 2, 3, 4],
                "ancestor_id": [0, 0, 0, 1, 1],
            }
        ),
        lazy,
    )

    result = _collect(alifestd_mark_num_children_polars(df_pl))

    assert result["num_children"].to_list() == [2, 2, 0, 0, 0]


def test_alifestd_mark_num_children_polars_two_roots(lazy):
    """Two independent roots with children."""
    df_pl = _apply_lazy(
        pl.DataFrame(
            {
                "id": [0, 1, 2, 3],
                "ancestor_id": [0, 1, 0, 1],
            }
        ),
        lazy,
    )

    result = _collect(alifestd_mark_num_children_polars(df_pl))

    assert result["num_children"].to_list() == [1, 1, 0, 0]


def test_alifestd_mark_num_children_polars_all_roots(lazy):
    """All self-referencing roots have 0 children."""
    df_pl = _apply_lazy(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_id": [0, 1, 2],
            }
        ),
        lazy,
    )

    result = _collect(alifestd_mark_num_children_polars(df_pl))

    assert result["num_children"].to_list() == [0, 0, 0]


def test_alifestd_mark_num_children_polars_single_node(lazy):
    """A single root node has 0 children."""
    df_pl = _apply_lazy(
        pl.DataFrame(
            {
                "id": [0],
                "ancestor_id": [0],
            }
        ),
        lazy,
    )

    result = _collect(alifestd_mark_num_children_polars(df_pl))

    assert result["num_children"].to_list() == [0]


def test_alifestd_mark_num_children_polars_empty(lazy):
    """Empty dataframe gets num_children column."""
    df_pl = _apply_lazy(
        pl.DataFrame(
            {"id": [], "ancestor_id": []},
            schema={"id": pl.Int64, "ancestor_id": pl.Int64},
        ),
        lazy,
    )

    result = _collect(alifestd_mark_num_children_polars(df_pl))

    assert "num_children" in result.columns
    assert result.is_empty()


def test_alifestd_mark_num_children_polars_preserves_columns(lazy):
    """Verify original columns are preserved."""
    df_pl = _apply_lazy(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_id": [0, 0, 1],
                "origin_time": [0.0, 1.0, 2.0],
                "taxon_label": ["a", "b", "c"],
            }
        ),
        lazy,
    )

    result = _collect(alifestd_mark_num_children_polars(df_pl))

    assert "num_children" in result.columns
    assert "origin_time" in result.columns
    assert "taxon_label" in result.columns
    assert result["origin_time"].to_list() == [0.0, 1.0, 2.0]
    assert result["taxon_label"].to_list() == ["a", "b", "c"]


def test_alifestd_mark_num_children_polars_does_not_mutate(lazy):
    """Verify the input dataframe is not mutated."""
    df_eager = pl.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [0, 0, 0, 1],
        }
    )
    df_pl = _apply_lazy(df_eager, lazy)

    original_cols = df_eager.columns[:]
    original_len = len(df_eager)

    _ = _collect(alifestd_mark_num_children_polars(df_pl))

    assert len(df_eager) == original_len
    assert df_eager.columns == original_cols


def test_alifestd_mark_num_children_polars_with_preexisting_is_root(lazy):
    """If is_root already exists, it should be used directly."""
    df_pl = _apply_lazy(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_id": [0, 0, 1],
                "is_root": [True, False, False],
            }
        ),
        lazy,
    )

    result = _collect(alifestd_mark_num_children_polars(df_pl))

    assert result["num_children"].to_list() == [1, 1, 0]


def test_alifestd_mark_num_children_polars_non_contiguous_ids(lazy):
    """Verify NotImplementedError for non-contiguous ids."""
    df_pl = _apply_lazy(
        pl.DataFrame(
            {
                "id": [0, 2, 5],
                "ancestor_id": [0, 0, 2],
            }
        ),
        lazy,
    )
    with pytest.raises(NotImplementedError):
        _collect(alifestd_mark_num_children_polars(df_pl))


def test_alifestd_mark_num_children_polars_unsorted(lazy):
    """Verify NotImplementedError for topologically unsorted data."""
    df_pl = _apply_lazy(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_id": [0, 2, 0],
            }
        ),
        lazy,
    )
    with pytest.raises(NotImplementedError):
        _collect(alifestd_mark_num_children_polars(df_pl))


def test_alifestd_mark_num_children_polars_star_topology(lazy):
    """Root with many direct children."""
    df_pl = _apply_lazy(
        pl.DataFrame(
            {
                "id": [0, 1, 2, 3, 4, 5],
                "ancestor_id": [0, 0, 0, 0, 0, 0],
            }
        ),
        lazy,
    )

    result = _collect(alifestd_mark_num_children_polars(df_pl))

    assert result["num_children"].to_list() == [5, 0, 0, 0, 0, 0]
