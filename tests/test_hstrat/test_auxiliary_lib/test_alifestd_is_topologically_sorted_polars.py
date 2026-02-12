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
def test_alifestd_is_topologically_sorted_polars_true(phylogeny_df, apply):
    """Topologically sorted + contiguous ids should return True."""
    df = apply(_prepare_polars(phylogeny_df))
    assert alifestd_is_topologically_sorted_polars(df)


@pytest.mark.parametrize(
    "ids,ancestor_ids",
    [
        ([0, 1, 2], [0, 2, 0]),  # node 1 has ancestor 2 > 1
        ([0, 1, 2, 3], [0, 0, 3, 0]),  # node 2 has ancestor 3 > 2
        ([0, 1, 2, 3, 4], [0, 0, 0, 4, 1]),  # node 3 has ancestor 4 > 3
    ],
)
@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_is_topologically_sorted_polars_false(
    ids, ancestor_ids, apply
):
    """Data with sorted ids but invalid topological order should be False."""
    df = apply(
        pl.DataFrame({"id": ids, "ancestor_id": ancestor_ids}),
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
@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_is_topologically_sorted_polars_matches_pandas(
    phylogeny_df, apply
):
    """Verify polars result matches pandas result for sorted input."""
    phylogeny_df_pd = alifestd_try_add_ancestor_id_col(phylogeny_df.copy())
    phylogeny_df_pd = alifestd_topological_sort(phylogeny_df_pd)
    phylogeny_df_pd = alifestd_assign_contiguous_ids(phylogeny_df_pd)

    result_pd = alifestd_is_topologically_sorted(phylogeny_df_pd)

    df = apply(pl.from_pandas(phylogeny_df_pd))
    result_pl = alifestd_is_topologically_sorted_polars(df)

    assert result_pd == result_pl


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_is_topologically_sorted_polars_simple_sorted(apply):
    """Simple chain 0 -> 1 -> 2 is topologically sorted."""
    df = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_id": [0, 0, 1],
            }
        ),
    )
    assert alifestd_is_topologically_sorted_polars(df)


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_is_topologically_sorted_polars_simple_unsorted(apply):
    """Node 1 has ancestor_id 2 which is > 1, so not topologically sorted."""
    df = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_id": [0, 2, 0],
            }
        ),
    )
    assert not alifestd_is_topologically_sorted_polars(df)


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_is_topologically_sorted_polars_simple_tree(apply):
    """Test a simple tree.

    Tree structure:
        0 (root)
        +-- 1
        |   +-- 3
        |   +-- 4
        +-- 2
    """
    df = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2, 3, 4],
                "ancestor_id": [0, 0, 0, 1, 1],
            }
        ),
    )
    assert alifestd_is_topologically_sorted_polars(df)


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_is_topologically_sorted_polars_single_node(apply):
    """A single root node is topologically sorted."""
    df = apply(
        pl.DataFrame(
            {
                "id": [0],
                "ancestor_id": [0],
            }
        ),
    )
    assert alifestd_is_topologically_sorted_polars(df)


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_is_topologically_sorted_polars_two_roots(apply):
    """Two independent roots, sorted."""
    df = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2, 3],
                "ancestor_id": [0, 1, 0, 1],
            }
        ),
    )
    assert alifestd_is_topologically_sorted_polars(df)


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_is_topologically_sorted_polars_all_roots(apply):
    """All self-referencing roots are topologically sorted."""
    df = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_id": [0, 1, 2],
            }
        ),
    )
    assert alifestd_is_topologically_sorted_polars(df)


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_is_topologically_sorted_polars_empty(apply):
    """Empty dataframe is topologically sorted."""
    df = apply(
        pl.DataFrame(
            {"id": [], "ancestor_id": []},
            schema={"id": pl.Int64, "ancestor_id": pl.Int64},
        ),
    )
    assert alifestd_is_topologically_sorted_polars(df)


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_is_topologically_sorted_polars_no_ancestor_id(apply):
    """Verify NotImplementedError for missing ancestor_id."""
    df = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_list": ["[none]", "[0]", "[1]"],
            }
        ),
    )
    with pytest.raises(NotImplementedError):
        alifestd_is_topologically_sorted_polars(df)


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_is_topologically_sorted_polars_unsorted_ids(apply):
    """Verify NotImplementedError for unsorted id values."""
    df = apply(
        pl.DataFrame(
            {
                "id": [2, 0, 1],
                "ancestor_id": [0, 0, 0],
            }
        ),
    )
    with pytest.raises(NotImplementedError):
        alifestd_is_topologically_sorted_polars(df)
