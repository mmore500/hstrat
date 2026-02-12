import os
import typing

import pandas as pd
import polars as pl
import pytest

from hstrat._auxiliary_lib import (
    alifestd_aggregate_phylogenies,
    alifestd_assign_contiguous_ids,
    alifestd_downsample_tips_asexual,
    alifestd_topological_sort,
    alifestd_try_add_ancestor_id_col,
)
from hstrat._auxiliary_lib._alifestd_downsample_tips_polars import (
    alifestd_downsample_tips_polars,
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


def _count_leaf_nodes_polars(phylogeny_df: pl.DataFrame) -> int:
    """Count leaf nodes in a polars dataframe (works with any ids)."""
    all_ids = set(phylogeny_df["id"].to_list())
    # internal nodes are those that appear as ancestor_id of some other node
    # (exclude root self-references)
    internal_ids = set(
        phylogeny_df.filter(pl.col("ancestor_id") != pl.col("id"))
        .select("ancestor_id")
        .to_series()
        .to_list()
    )
    return len(all_ids - internal_ids)


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        alifestd_aggregate_phylogenies(
            [
                pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
                pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
            ]
        ),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
@pytest.mark.parametrize("n_downsample", [1, 5, 10, 100000000])
@pytest.mark.parametrize("seed", [1, 42])
@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_downsample_tips_polars(
    phylogeny_df: pd.DataFrame,
    n_downsample: int,
    seed: int,
    apply: typing.Callable,
):
    phylogeny_df_pl = apply(_prepare_polars(phylogeny_df))

    original_len = len(phylogeny_df_pl.lazy().collect())
    original_num_tips = _count_leaf_nodes_polars(
        phylogeny_df_pl.lazy().collect()
    )

    result_df = (
        alifestd_downsample_tips_polars(
            phylogeny_df_pl,
            n_downsample,
            seed=seed,
        )
        .lazy()
        .collect()
    )

    assert len(result_df) <= original_len
    assert "extant" not in result_df.columns
    assert set(result_df["id"].to_list()).issubset(
        set(phylogeny_df_pl.lazy().collect()["id"].to_list())
    )
    assert _count_leaf_nodes_polars(result_df) == min(
        original_num_tips, n_downsample
    )


@pytest.mark.parametrize("n_downsample", [0, 1])
@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_downsample_tips_polars_empty(
    n_downsample: int, apply: typing.Callable
):
    phylogeny_df = apply(
        pl.DataFrame(
            {"id": [], "ancestor_id": []},
            schema={"id": pl.Int64, "ancestor_id": pl.Int64},
        ),
    )

    result_df = (
        alifestd_downsample_tips_polars(
            phylogeny_df,
            n_downsample,
        )
        .lazy()
        .collect()
    )

    assert result_df.is_empty()


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        alifestd_aggregate_phylogenies(
            [
                pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
                pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
            ]
        ),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
@pytest.mark.parametrize("n_downsample", [1, 5, 10])
@pytest.mark.parametrize("seed", [1, 42])
@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_downsample_tips_polars_matches_pandas(
    phylogeny_df: pd.DataFrame,
    n_downsample: int,
    seed: int,
    apply: typing.Callable,
):
    """Verify polars result has same structure as pandas result."""
    phylogeny_df_pd = alifestd_try_add_ancestor_id_col(phylogeny_df.copy())
    phylogeny_df_pd = alifestd_topological_sort(phylogeny_df_pd)
    phylogeny_df_pd = alifestd_assign_contiguous_ids(phylogeny_df_pd)

    phylogeny_df_pl = apply(pl.from_pandas(phylogeny_df_pd))

    alifestd_downsample_tips_asexual(
        phylogeny_df_pd,
        n_downsample,
        mutate=False,
        seed=seed,
    )
    result_pl = (
        alifestd_downsample_tips_polars(
            phylogeny_df_pl,
            n_downsample,
            seed=seed,
        )
        .lazy()
        .collect()
    )

    assert _count_leaf_nodes_polars(result_pl) == min(
        n_downsample,
        _count_leaf_nodes_polars(pl.from_pandas(phylogeny_df_pd)),
    )
    assert set(result_pl["id"].to_list()).issubset(
        set(phylogeny_df_pl.lazy().collect()["id"].to_list())
    )


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
@pytest.mark.parametrize("seed", [1, 42])
@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_downsample_tips_polars_deterministic(
    phylogeny_df: pd.DataFrame,
    seed: int,
    apply: typing.Callable,
):
    """Verify same seed produces same result."""
    phylogeny_df_pl = apply(_prepare_polars(phylogeny_df))

    result1 = (
        alifestd_downsample_tips_polars(
            phylogeny_df_pl,
            5,
            seed=seed,
        )
        .lazy()
        .collect()
    )
    result2 = (
        alifestd_downsample_tips_polars(
            phylogeny_df_pl,
            5,
            seed=seed,
        )
        .lazy()
        .collect()
    )

    assert result1["id"].to_list() == result2["id"].to_list()


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_downsample_tips_polars_no_ancestor_id(
    apply: typing.Callable,
):
    df = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_list": ["[none]", "[0]", "[1]"],
            }
        ),
    )
    with pytest.raises(NotImplementedError):
        alifestd_downsample_tips_polars(df, 1)


def test_alifestd_downsample_tips_polars_does_not_mutate():
    """Verify the input dataframe is not mutated."""
    df = pl.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [0, 0, 0, 1],
            "destruction_time": [float("inf")] * 4,
        }
    )

    original_len = len(df)
    original_cols = df.columns

    _ = alifestd_downsample_tips_polars(df, 2, seed=1).lazy().collect()

    assert len(df) == original_len
    assert df.columns == original_cols


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_downsample_tips_polars_simple(apply: typing.Callable):
    """Test a simple hand-crafted tree.

    Tree structure:
        0 (root)
        +-- 1
        |   +-- 3 (leaf)
        |   +-- 4 (leaf)
        +-- 2 (leaf)

    Downsample to 1 tip should keep exactly one leaf and its lineage.
    """
    df = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2, 3, 4],
                "ancestor_id": [0, 0, 0, 1, 1],
                "destruction_time": [float("inf")] * 5,
            }
        ),
    )

    result = alifestd_downsample_tips_polars(df, 1, seed=1).lazy().collect()

    assert _count_leaf_nodes_polars(result) == 1
    assert 0 in result["id"].to_list()  # root must be present


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_downsample_tips_polars_all_tips(apply: typing.Callable):
    """Requesting more tips than exist should return the full phylogeny."""
    df = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2, 3, 4],
                "ancestor_id": [0, 0, 0, 1, 1],
                "destruction_time": [float("inf")] * 5,
            }
        ),
    )

    result = (
        alifestd_downsample_tips_polars(
            df,
            100000,
            seed=1,
        )
        .lazy()
        .collect()
    )

    assert len(result) == 5
