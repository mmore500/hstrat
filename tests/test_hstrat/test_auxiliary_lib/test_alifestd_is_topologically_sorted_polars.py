import os

import pandas as pd
import polars as pl
import pytest

from hstrat._auxiliary_lib import (
    alifestd_assign_contiguous_ids,
    alifestd_is_topologically_sorted,
    alifestd_topological_sort,
    alifestd_try_add_ancestor_id_col,
)
from hstrat._auxiliary_lib._alifestd_is_topologically_sorted_polars import (
    alifestd_is_topologically_sorted_polars,
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
def test_alifestd_is_topologically_sorted_polars_true(phylogeny_df, lazy):
    """Topologically sorted + contiguous ids should return True."""
    df = _apply_lazy(_prepare_polars(phylogeny_df), lazy)
    assert alifestd_is_topologically_sorted_polars(df)


@pytest.mark.parametrize(
    "ids,ancestor_ids",
    [
        ([0, 1, 2], [0, 2, 0]),  # node 1 has ancestor 2 > 1
        ([0, 1, 2, 3], [0, 0, 3, 0]),  # node 2 has ancestor 3 > 2
        ([0, 1, 2, 3, 4], [0, 0, 0, 4, 1]),  # node 3 has ancestor 4 > 3
    ],
)
def test_alifestd_is_topologically_sorted_polars_false(
    ids, ancestor_ids, lazy
):
    """Data with sorted ids but invalid topological order should be False."""
    df = _apply_lazy(
        pl.DataFrame({"id": ids, "ancestor_id": ancestor_ids}),
        lazy,
    )
    assert not alifestd_is_topologically_sorted_polars(df)


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
def test_alifestd_is_topologically_sorted_polars_matches_pandas(
    phylogeny_df, lazy
):
    """Verify polars result matches pandas result for sorted input."""
    phylogeny_df_pd = alifestd_try_add_ancestor_id_col(phylogeny_df.copy())
    phylogeny_df_pd = alifestd_topological_sort(phylogeny_df_pd)
    phylogeny_df_pd = alifestd_assign_contiguous_ids(phylogeny_df_pd)

    result_pd = alifestd_is_topologically_sorted(phylogeny_df_pd)

    df = _apply_lazy(pl.from_pandas(phylogeny_df_pd), lazy)
    result_pl = alifestd_is_topologically_sorted_polars(df)

    assert result_pd == result_pl


def test_alifestd_is_topologically_sorted_polars_simple_sorted(lazy):
    """Simple chain 0 -> 1 -> 2 is topologically sorted."""
    df = _apply_lazy(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_id": [0, 0, 1],
            }
        ),
        lazy,
    )
    assert alifestd_is_topologically_sorted_polars(df)


def test_alifestd_is_topologically_sorted_polars_simple_unsorted(lazy):
    """Node 1 has ancestor_id 2 which is > 1, so not topologically sorted."""
    df = _apply_lazy(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_id": [0, 2, 0],
            }
        ),
        lazy,
    )
    assert not alifestd_is_topologically_sorted_polars(df)


def test_alifestd_is_topologically_sorted_polars_simple_tree(lazy):
    """Test a simple tree.

    Tree structure:
        0 (root)
        +-- 1
        |   +-- 3
        |   +-- 4
        +-- 2
    """
    df = _apply_lazy(
        pl.DataFrame(
            {
                "id": [0, 1, 2, 3, 4],
                "ancestor_id": [0, 0, 0, 1, 1],
            }
        ),
        lazy,
    )
    assert alifestd_is_topologically_sorted_polars(df)


def test_alifestd_is_topologically_sorted_polars_single_node(lazy):
    """A single root node is topologically sorted."""
    df = _apply_lazy(
        pl.DataFrame(
            {
                "id": [0],
                "ancestor_id": [0],
            }
        ),
        lazy,
    )
    assert alifestd_is_topologically_sorted_polars(df)


def test_alifestd_is_topologically_sorted_polars_two_roots(lazy):
    """Two independent roots, sorted."""
    df = _apply_lazy(
        pl.DataFrame(
            {
                "id": [0, 1, 2, 3],
                "ancestor_id": [0, 1, 0, 1],
            }
        ),
        lazy,
    )
    assert alifestd_is_topologically_sorted_polars(df)


def test_alifestd_is_topologically_sorted_polars_all_roots(lazy):
    """All self-referencing roots are topologically sorted."""
    df = _apply_lazy(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_id": [0, 1, 2],
            }
        ),
        lazy,
    )
    assert alifestd_is_topologically_sorted_polars(df)


def test_alifestd_is_topologically_sorted_polars_empty(lazy):
    """Empty dataframe is topologically sorted."""
    df = _apply_lazy(
        pl.DataFrame(
            {"id": [], "ancestor_id": []},
            schema={"id": pl.Int64, "ancestor_id": pl.Int64},
        ),
        lazy,
    )
    assert alifestd_is_topologically_sorted_polars(df)


def test_alifestd_is_topologically_sorted_polars_no_ancestor_id(lazy):
    """Verify NotImplementedError for missing ancestor_id."""
    df = _apply_lazy(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_list": ["[none]", "[0]", "[1]"],
            }
        ),
        lazy,
    )
    with pytest.raises(NotImplementedError):
        alifestd_is_topologically_sorted_polars(df)


def test_alifestd_is_topologically_sorted_polars_unsorted_ids(lazy):
    """Verify NotImplementedError for unsorted id values."""
    df = _apply_lazy(
        pl.DataFrame(
            {
                "id": [2, 0, 1],
                "ancestor_id": [0, 0, 0],
            }
        ),
        lazy,
    )
    with pytest.raises(NotImplementedError):
        alifestd_is_topologically_sorted_polars(df)
