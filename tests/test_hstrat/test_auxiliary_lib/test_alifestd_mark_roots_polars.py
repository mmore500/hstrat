import os

import pandas as pd
import polars as pl
import pytest

from hstrat._auxiliary_lib import (
    alifestd_assign_contiguous_ids,
    alifestd_mark_roots,
    alifestd_topological_sort,
    alifestd_try_add_ancestor_id_col,
)
from hstrat._auxiliary_lib._alifestd_mark_roots_polars import (
    alifestd_mark_roots_polars,
)

pytestmark = pytest.mark.filterwarnings(
    "ignore::polars.exceptions.PerformanceWarning"
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


def _prepare_polars(phylogeny_df_pd: pd.DataFrame) -> pl.DataFrame:
    """Prepare a pandas phylogeny dataframe for the polars implementation."""
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
def test_alifestd_mark_roots_polars_fuzz(phylogeny_df, apply):
    """Verify is_root marks match known root ids."""
    df_prepared = _prepare_polars(phylogeny_df)
    df_pl = apply(df_prepared)

    result = alifestd_mark_roots_polars(df_pl).lazy().collect()

    assert "is_root" in result.columns
    assert len(result) == len(df_prepared)

    # roots are nodes where id == ancestor_id
    expected_root_ids = set(
        df_prepared.filter(
            pl.col("id") == pl.col("ancestor_id"),
        )["id"].to_list()
    )
    for row in result.iter_rows(named=True):
        if row["id"] in expected_root_ids:
            assert row["is_root"]
        else:
            assert not row["is_root"]


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
def test_alifestd_mark_roots_polars_matches_pandas(phylogeny_df, apply):
    """Verify polars result matches pandas result."""
    phylogeny_df_pd = alifestd_try_add_ancestor_id_col(phylogeny_df.copy())
    phylogeny_df_pd = alifestd_topological_sort(phylogeny_df_pd)
    phylogeny_df_pd = alifestd_assign_contiguous_ids(phylogeny_df_pd)

    result_pd = alifestd_mark_roots(phylogeny_df_pd, mutate=False)

    df_pl = apply(pl.from_pandas(phylogeny_df_pd))
    result_pl = alifestd_mark_roots_polars(df_pl).lazy().collect()

    root_ids_pd = set(
        result_pd[result_pd["is_root"]]["id"],
    )
    root_ids_pl = set(
        result_pl.filter(pl.col("is_root"))["id"].to_list(),
    )
    assert root_ids_pd == root_ids_pl


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_mark_roots_polars_simple(apply):
    """Test simple chain: only node 0 is root."""
    df = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_id": [0, 0, 1],
            }
        ),
    )

    result = alifestd_mark_roots_polars(df).lazy().collect()

    assert result["is_root"].to_list() == [True, False, False]


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_mark_roots_polars_simple_tree(apply):
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

    result = alifestd_mark_roots_polars(df).lazy().collect()

    assert result["is_root"].to_list() == [True, False, False, False, False]


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_mark_roots_polars_two_roots(apply):
    """Two independent root nodes."""
    df = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2, 3],
                "ancestor_id": [0, 1, 0, 1],
            }
        ),
    )

    result = alifestd_mark_roots_polars(df).lazy().collect()

    assert result["is_root"].to_list() == [True, True, False, False]


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_mark_roots_polars_all_roots(apply):
    """All self-referencing nodes are roots."""
    df = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_id": [0, 1, 2],
            }
        ),
    )

    result = alifestd_mark_roots_polars(df).lazy().collect()

    assert result["is_root"].to_list() == [True, True, True]


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_mark_roots_polars_single_node(apply):
    """A single root node."""
    df = apply(
        pl.DataFrame(
            {
                "id": [0],
                "ancestor_id": [0],
            }
        ),
    )

    result = alifestd_mark_roots_polars(df).lazy().collect()

    assert result["is_root"].to_list() == [True]


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_mark_roots_polars_empty(apply):
    """Empty dataframe gets is_root column."""
    df = apply(
        pl.DataFrame(
            {"id": [], "ancestor_id": []},
            schema={"id": pl.Int64, "ancestor_id": pl.Int64},
        ),
    )

    result = alifestd_mark_roots_polars(df).lazy().collect()

    assert "is_root" in result.columns
    assert result.is_empty()


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_mark_roots_polars_no_ancestor_id(apply):
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
        alifestd_mark_roots_polars(df).lazy().collect()


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_mark_roots_polars_preserves_columns(apply):
    """Verify original columns are preserved."""
    df = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_id": [0, 0, 1],
                "origin_time": [0.0, 1.0, 2.0],
                "taxon_label": ["a", "b", "c"],
            }
        ),
    )

    result = alifestd_mark_roots_polars(df).lazy().collect()

    assert "is_root" in result.columns
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
def test_alifestd_mark_roots_polars_does_not_mutate(apply):
    """Verify the input dataframe is not mutated."""
    df_eager = pl.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_id": [0, 0, 1],
        }
    )
    df = apply(df_eager)

    original_cols = df_eager.columns[:]
    original_len = len(df_eager)

    _ = alifestd_mark_roots_polars(df).lazy().collect()

    assert len(df_eager) == original_len
    assert df_eager.columns == original_cols
