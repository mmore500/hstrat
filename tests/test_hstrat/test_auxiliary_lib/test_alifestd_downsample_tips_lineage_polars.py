import os
import typing

import pandas as pd
import polars as pl
import pytest

from hstrat._auxiliary_lib import (
    alifestd_aggregate_phylogenies,
    alifestd_downsample_tips_lineage_asexual,
    alifestd_to_working_format,
)
from hstrat._auxiliary_lib._alifestd_assign_contiguous_ids_polars import (
    alifestd_assign_contiguous_ids_polars,
)
from hstrat._auxiliary_lib._alifestd_downsample_tips_lineage_polars import (
    alifestd_downsample_tips_lineage_polars,
)
from hstrat._auxiliary_lib._alifestd_mark_leaves_polars import (
    alifestd_mark_leaves_polars,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv")
        ),
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv")
        ),
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_tournamentselection.csv")
        ),
    ],
)
@pytest.mark.parametrize("num_tips", [1, 5, 10, 100000000])
@pytest.mark.parametrize("seed", [1, 42])
@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_downsample_tips_lineage_polars(
    phylogeny_df: pd.DataFrame,
    num_tips: int,
    seed: int,
    apply: typing.Callable,
):
    phylogeny_df_pl = apply(pl.from_pandas(phylogeny_df))

    original_len = len(phylogeny_df_pl.lazy().collect())
    original_num_tips = (
        alifestd_mark_leaves_polars(phylogeny_df_pl)
        .lazy()
        .select(pl.col("is_leaf").sum())
        .collect()
        .item()
    )

    result_df = (
        alifestd_downsample_tips_lineage_polars(
            phylogeny_df_pl,
            num_tips,
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
    result_num_tips = (
        alifestd_mark_leaves_polars(
            alifestd_assign_contiguous_ids_polars(
                result_df.select("id", "ancestor_id"),
            ),
        )
        .lazy()
        .select(pl.col("is_leaf").sum())
        .collect()
        .item()
    )
    assert result_num_tips <= min(original_num_tips, num_tips)


@pytest.mark.parametrize("num_tips", [0, 1])
@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_downsample_tips_lineage_polars_empty(
    num_tips: int, apply: typing.Callable
):
    phylogeny_df = apply(
        pl.DataFrame(
            {
                "id": [],
                "ancestor_id": [],
                "origin_time": [],
            },
            schema={
                "id": pl.Int64,
                "ancestor_id": pl.Int64,
                "origin_time": pl.Float64,
            },
        ),
    )

    result_df = (
        alifestd_downsample_tips_lineage_polars(
            phylogeny_df,
            num_tips,
        )
        .lazy()
        .collect()
    )

    assert result_df.is_empty()


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv")
        ),
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv")
        ),
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_tournamentselection.csv")
        ),
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
def test_alifestd_downsample_tips_lineage_polars_deterministic(
    phylogeny_df: pd.DataFrame,
    seed: int,
    apply: typing.Callable,
):
    """Verify same seed produces same result."""
    phylogeny_df_pl = apply(pl.from_pandas(phylogeny_df))

    result1 = (
        alifestd_downsample_tips_lineage_polars(
            phylogeny_df_pl,
            5,
            seed=seed,
        )
        .lazy()
        .collect()
    )
    result2 = (
        alifestd_downsample_tips_lineage_polars(
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
def test_alifestd_downsample_tips_lineage_polars_with_ancestor_id(
    apply: typing.Callable,
):
    """Test with explicit ancestor_id column."""
    df = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_id": [0, 0, 1],
                "origin_time": [0.0, 1.0, 2.0],
                "destruction_time": [float("inf")] * 3,
            }
        ),
    )
    result = (
        alifestd_downsample_tips_lineage_polars(df, 1, seed=1)
        .lazy()
        .collect()
    )
    assert len(result) >= 1


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_downsample_tips_lineage_polars_missing_criterion(
    apply: typing.Callable,
):
    df = apply(
        pl.DataFrame(
            {
                "id": [0, 1],
                "ancestor_id": [0, 0],
                "origin_time": [0.0, 1.0],
            }
        ),
    )
    with pytest.raises(ValueError, match="criterion column"):
        alifestd_downsample_tips_lineage_polars(
            df, 1, criterion_delta="nonexistent"
        )


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv")
        ),
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv")
        ),
    ],
)
@pytest.mark.parametrize("num_tips", [1, 5, 10])
@pytest.mark.parametrize("seed", [1, 42])
@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_downsample_tips_lineage_polars_matches_pandas(
    phylogeny_df: pd.DataFrame,
    num_tips: int,
    seed: int,
    apply: typing.Callable,
):
    """Verify polars result has same structure as pandas result."""
    phylogeny_df_pl = apply(pl.from_pandas(phylogeny_df))

    result_pd = alifestd_downsample_tips_lineage_asexual(
        phylogeny_df,
        num_tips,
        mutate=False,
        seed=seed,
    )
    result_pl = (
        alifestd_downsample_tips_lineage_polars(
            phylogeny_df_pl,
            num_tips,
            seed=seed,
        )
        .lazy()
        .collect()
    )

    result_num_tips_pl = (
        alifestd_mark_leaves_polars(
            alifestd_assign_contiguous_ids_polars(
                result_pl.select("id", "ancestor_id"),
            ),
        )
        .lazy()
        .select(pl.col("is_leaf").sum())
        .collect()
        .item()
    )
    original_num_tips = (
        alifestd_mark_leaves_polars(pl.from_pandas(phylogeny_df))
        .lazy()
        .select(pl.col("is_leaf").sum())
        .collect()
        .item()
    )
    assert result_num_tips_pl == min(num_tips, original_num_tips)
    assert set(result_pl["id"].to_list()).issubset(
        set(phylogeny_df_pl.lazy().collect()["id"].to_list())
    )

    # Both should produce same leaf count
    from hstrat._auxiliary_lib import alifestd_count_leaf_nodes

    assert result_num_tips_pl == alifestd_count_leaf_nodes(result_pd)


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_downsample_tips_lineage_polars_simple(
    apply: typing.Callable,
):
    """Test a simple hand-crafted tree.

    Tree structure:
        0 (root, origin_time=0)
        +-- 1 (origin_time=1)
        |   +-- 3 (leaf, origin_time=3)
        |   +-- 4 (leaf, origin_time=4)
        +-- 2 (leaf, origin_time=2)

    Target leaf should be 4 (largest origin_time).
    Downsample to 1 tip should keep exactly one leaf and its lineage.
    """
    df = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2, 3, 4],
                "ancestor_id": [0, 0, 0, 1, 1],
                "origin_time": [0.0, 1.0, 2.0, 3.0, 4.0],
                "destruction_time": [float("inf")] * 5,
            }
        ),
    )

    result = (
        alifestd_downsample_tips_lineage_polars(df, 1, seed=1)
        .lazy()
        .collect()
    )

    result_num_tips = (
        alifestd_mark_leaves_polars(
            alifestd_assign_contiguous_ids_polars(
                result.select("id", "ancestor_id"),
            ),
        )
        .lazy()
        .select(pl.col("is_leaf").sum())
        .collect()
        .item()
    )
    assert result_num_tips == 1
    assert 0 in result["id"].to_list()  # root must be present


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_downsample_tips_lineage_polars_all_tips(
    apply: typing.Callable,
):
    """Requesting more tips than exist should return the full phylogeny."""
    df = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2, 3, 4],
                "ancestor_id": [0, 0, 0, 1, 1],
                "origin_time": [0.0, 1.0, 2.0, 3.0, 4.0],
                "destruction_time": [float("inf")] * 5,
            }
        ),
    )

    result = (
        alifestd_downsample_tips_lineage_polars(
            df,
            100000,
            seed=1,
        )
        .lazy()
        .collect()
    )

    assert len(result) == 5


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_downsample_tips_lineage_polars_no_temp_cols(
    apply: typing.Callable,
):
    """Ensure no internal temporary columns leak into the output."""
    phylogeny_df = alifestd_to_working_format(
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
    )
    phylogeny_df_pl = apply(pl.from_pandas(phylogeny_df))

    result_df = (
        alifestd_downsample_tips_lineage_polars(
            phylogeny_df_pl, 5, seed=1,
        )
        .lazy()
        .collect()
    )

    for col in result_df.columns:
        assert not col.startswith("_alifestd_downsample")
        assert col != "_delta"


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv")
        ),
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv")
        ),
    ],
)
def test_alifestd_downsample_tips_lineage_polars_custom_criterion(
    phylogeny_df,
):
    phylogeny_df_pl = pl.from_pandas(phylogeny_df)

    result_df = (
        alifestd_downsample_tips_lineage_polars(
            phylogeny_df_pl,
            5,
            seed=1,
            criterion_delta="origin_time",
            criterion_target="origin_time",
        )
        .lazy()
        .collect()
    )

    result_num_tips = (
        alifestd_mark_leaves_polars(
            alifestd_assign_contiguous_ids_polars(
                result_df.select("id", "ancestor_id"),
            ),
        )
        .lazy()
        .select(pl.col("is_leaf").sum())
        .collect()
        .item()
    )
    assert result_num_tips == 5
    assert set(result_df["id"].to_list()).issubset(
        set(phylogeny_df_pl["id"].to_list())
    )
