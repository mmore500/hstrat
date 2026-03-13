import os
import typing

import numpy as np
import pandas as pd
import polars as pl
import pytest

from hstrat._auxiliary_lib import (
    alifestd_downsample_tips_lineage_stratified_asexual,
    alifestd_sum_origin_time_deltas_asexual,
    alifestd_to_working_format,
)
from hstrat._auxiliary_lib._alifestd_assign_contiguous_ids_polars import (
    alifestd_assign_contiguous_ids_polars,
)
from hstrat._auxiliary_lib._alifestd_downsample_tips_lineage_stratified_polars import (
    alifestd_downsample_tips_lineage_stratified_polars,
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
@pytest.mark.parametrize("n_tips", [None, 1, 5, 10])
@pytest.mark.parametrize("seed", [1, 42])
@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_downsample_tips_lineage_stratified_polars(
    phylogeny_df: pd.DataFrame,
    n_tips: typing.Optional[int],
    seed: int,
    apply: typing.Callable,
):
    phylogeny_df_pl = apply(pl.from_pandas(phylogeny_df))

    original_len = len(phylogeny_df_pl.lazy().collect())

    result_df = (
        alifestd_downsample_tips_lineage_stratified_polars(
            phylogeny_df_pl,
            n_tips,
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


@pytest.mark.parametrize("n_tips", [None, 1])
@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_downsample_tips_lineage_stratified_polars_empty(
    n_tips: typing.Optional[int], apply: typing.Callable
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
        alifestd_downsample_tips_lineage_stratified_polars(
            phylogeny_df,
            n_tips,
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
def test_alifestd_downsample_tips_lineage_stratified_polars_deterministic(
    phylogeny_df: pd.DataFrame,
    seed: int,
    apply: typing.Callable,
):
    """Verify same seed produces same result."""
    phylogeny_df_pl = apply(pl.from_pandas(phylogeny_df))

    result1 = (
        alifestd_downsample_tips_lineage_stratified_polars(
            phylogeny_df_pl,
            5,
            seed=seed,
        )
        .lazy()
        .collect()
    )
    result2 = (
        alifestd_downsample_tips_lineage_stratified_polars(
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
def test_alifestd_downsample_tips_lineage_stratified_polars_with_ancestor_id(
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
        alifestd_downsample_tips_lineage_stratified_polars(df, seed=1)
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
def test_alifestd_downsample_tips_lineage_stratified_polars_missing_criterion(
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
        alifestd_downsample_tips_lineage_stratified_polars(
            df, criterion_delta="nonexistent"
        )

    with pytest.raises(ValueError, match="criterion column"):
        alifestd_downsample_tips_lineage_stratified_polars(
            df, criterion_stratify="nonexistent"
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
@pytest.mark.parametrize("seed", [1, 42])
@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_downsample_tips_lineage_stratified_polars_matches_pandas(
    phylogeny_df: pd.DataFrame,
    seed: int,
    apply: typing.Callable,
):
    """Verify polars result has same structure as pandas result."""
    phylogeny_df_pl = apply(pl.from_pandas(phylogeny_df))

    result_pd = alifestd_downsample_tips_lineage_stratified_asexual(
        phylogeny_df,
        5,
        mutate=False,
        seed=seed,
    )
    result_pl = (
        alifestd_downsample_tips_lineage_stratified_polars(
            phylogeny_df_pl,
            5,
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
def test_alifestd_downsample_tips_lineage_stratified_polars_simple(
    apply: typing.Callable,
):
    """Test a simple hand-crafted tree.

    Tree structure:
        0 (root, origin_time=0)
        +-- 1 (origin_time=1)
        |   +-- 3 (leaf, origin_time=3)
        |   +-- 4 (leaf, origin_time=4)
        +-- 2 (leaf, origin_time=2)

    All leaves have distinct origin_times, so with n_tips=None each
    gets its own group => all 3 leaves retained.
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
        alifestd_downsample_tips_lineage_stratified_polars(df, seed=1)
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
    assert result_num_tips == 3
    assert 0 in result["id"].to_list()  # root must be present


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_downsample_tips_lineage_stratified_polars_n_tips_coarsening(
    apply: typing.Callable,
):
    """Test that n_tips coarsens stratified values via rank + integer division.

    Tree structure:
        0 (root, origin_time=0)
        +-- 1 (origin_time=1)
        |   +-- 3 (leaf, origin_time=3)
        |   +-- 4 (leaf, origin_time=4)
        +-- 2 (leaf, origin_time=2)

    Leaves at origin_time 2, 3, 4 (3 distinct strata).
    - n_tips=3: 3 groups => 3 leaves
    - n_tips=2: 2 groups => 2 leaves
    - n_tips=1: 1 group => 1 leaf
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

    result3 = (
        alifestd_downsample_tips_lineage_stratified_polars(
            df, n_tips=3, seed=1
        )
        .lazy()
        .collect()
    )
    result3_num_tips = (
        alifestd_mark_leaves_polars(
            alifestd_assign_contiguous_ids_polars(
                result3.select("id", "ancestor_id"),
            ),
        )
        .lazy()
        .select(pl.col("is_leaf").sum())
        .collect()
        .item()
    )
    assert result3_num_tips == 3

    result2 = (
        alifestd_downsample_tips_lineage_stratified_polars(
            df, n_tips=2, seed=1
        )
        .lazy()
        .collect()
    )
    result2_num_tips = (
        alifestd_mark_leaves_polars(
            alifestd_assign_contiguous_ids_polars(
                result2.select("id", "ancestor_id"),
            ),
        )
        .lazy()
        .select(pl.col("is_leaf").sum())
        .collect()
        .item()
    )
    assert result2_num_tips == 2

    result1 = (
        alifestd_downsample_tips_lineage_stratified_polars(
            df, n_tips=1, seed=1
        )
        .lazy()
        .collect()
    )
    result1_num_tips = (
        alifestd_mark_leaves_polars(
            alifestd_assign_contiguous_ids_polars(
                result1.select("id", "ancestor_id"),
            ),
        )
        .lazy()
        .select(pl.col("is_leaf").sum())
        .collect()
        .item()
    )
    assert result1_num_tips == 1


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_downsample_tips_lineage_stratified_polars_shared_stratum(
    apply: typing.Callable,
):
    """Test where multiple leaves share the same stratum value.

    Tree structure:
        0 (root, origin_time=0)
        +-- 1 (origin_time=1)
        |   +-- 3 (leaf, origin_time=2)
        |   +-- 4 (leaf, origin_time=2)
        +-- 2 (leaf, origin_time=2)

    All leaves share origin_time=2, so there is only 1 unique stratum.
    Regardless of n_tips, only 1 group => 1 leaf retained.
    """
    df = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2, 3, 4],
                "ancestor_id": [0, 0, 0, 1, 1],
                "origin_time": [0.0, 1.0, 2.0, 2.0, 2.0],
                "destruction_time": [float("inf")] * 5,
            }
        ),
    )

    result_none = (
        alifestd_downsample_tips_lineage_stratified_polars(df, seed=1)
        .lazy()
        .collect()
    )
    result_none_num_tips = (
        alifestd_mark_leaves_polars(
            alifestd_assign_contiguous_ids_polars(
                result_none.select("id", "ancestor_id"),
            ),
        )
        .lazy()
        .select(pl.col("is_leaf").sum())
        .collect()
        .item()
    )
    assert result_none_num_tips == 1

    result_big = (
        alifestd_downsample_tips_lineage_stratified_polars(
            df, n_tips=100, seed=1
        )
        .lazy()
        .collect()
    )
    result_big_num_tips = (
        alifestd_mark_leaves_polars(
            alifestd_assign_contiguous_ids_polars(
                result_big.select("id", "ancestor_id"),
            ),
        )
        .lazy()
        .select(pl.col("is_leaf").sum())
        .collect()
        .item()
    )
    assert result_big_num_tips == 1


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_downsample_tips_lineage_stratified_polars_all_tips(
    apply: typing.Callable,
):
    """n_tips larger than distinct values should keep all leaves."""
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
        alifestd_downsample_tips_lineage_stratified_polars(
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
def test_alifestd_downsample_tips_lineage_stratified_polars_no_temp_cols(
    apply: typing.Callable,
):
    """Ensure no internal temporary columns leak into the output."""
    phylogeny_df = alifestd_to_working_format(
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
    )
    phylogeny_df_pl = apply(pl.from_pandas(phylogeny_df))

    result_df = (
        alifestd_downsample_tips_lineage_stratified_polars(
            phylogeny_df_pl,
            5,
            seed=1,
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
def test_alifestd_downsample_tips_lineage_stratified_polars_custom_criterion(
    phylogeny_df,
):
    phylogeny_df_pl = pl.from_pandas(phylogeny_df)

    result_df = (
        alifestd_downsample_tips_lineage_stratified_polars(
            phylogeny_df_pl,
            5,
            seed=1,
            criterion_delta="origin_time",
            criterion_stratify="origin_time",
            criterion_target="origin_time",
        )
        .lazy()
        .collect()
    )

    assert len(result_df) >= 1
    assert set(result_df["id"].to_list()).issubset(
        set(phylogeny_df_pl["id"].to_list())
    )


def _count_tips_polars(result: pl.DataFrame) -> int:
    """Count leaf nodes in a polars result DataFrame."""
    return (
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


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_downsample_tips_lineage_stratified_polars_n_tips_per_stratum_validation(
    apply: typing.Callable,
):
    """n_tips_per_stratum must evenly divide n_tips."""
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

    with pytest.raises(ValueError, match="n_tips_per_stratum"):
        alifestd_downsample_tips_lineage_stratified_polars(
            df, n_tips=3, seed=1, n_tips_per_stratum=2
        )

    with pytest.raises(ValueError, match="n_tips_per_stratum"):
        alifestd_downsample_tips_lineage_stratified_polars(
            df, n_tips=5, seed=1, n_tips_per_stratum=3
        )


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_downsample_tips_lineage_stratified_polars_n_tips_per_stratum_basic(
    apply: typing.Callable,
):
    """Test n_tips_per_stratum picks correct number of tips per group."""
    df = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2, 3, 4, 5, 6],
                "ancestor_id": [0, 0, 0, 1, 1, 1, 1],
                "origin_time": [0.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0],
                "destruction_time": [float("inf")] * 7,
            }
        ),
    )

    result = (
        alifestd_downsample_tips_lineage_stratified_polars(
            df, seed=1, n_tips_per_stratum=2
        )
        .lazy()
        .collect()
    )
    assert _count_tips_polars(result) == 4

    result1 = (
        alifestd_downsample_tips_lineage_stratified_polars(
            df, seed=1, n_tips_per_stratum=1
        )
        .lazy()
        .collect()
    )
    assert _count_tips_polars(result1) == 2


@pytest.mark.parametrize(
    "apply",
    [
        pytest.param(lambda x: x, id="DataFrame"),
        pytest.param(lambda x: x.lazy(), id="LazyFrame"),
    ],
)
def test_alifestd_downsample_tips_lineage_stratified_polars_n_tips_per_stratum_with_n_tips(
    apply: typing.Callable,
):
    """Test n_tips_per_stratum combined with n_tips."""
    df = apply(
        pl.DataFrame(
            {
                "id": [0, 1, 2, 3, 4, 5, 6],
                "ancestor_id": [0, 0, 0, 1, 1, 1, 1],
                "origin_time": [0.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0],
                "destruction_time": [float("inf")] * 7,
            }
        ),
    )

    result = (
        alifestd_downsample_tips_lineage_stratified_polars(
            df, n_tips=4, seed=1, n_tips_per_stratum=2
        )
        .lazy()
        .collect()
    )
    assert _count_tips_polars(result) == 4


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
def test_alifestd_downsample_tips_lineage_stratified_polars_less_branch_length_than_random(
    phylogeny_df: pd.DataFrame,
):
    """Stratified downsampling should pull less total branch length (sum of
    origin_time deltas) than random tip sampling, on asset datasets with a
    spread of origin times.
    """
    n_tips = 5
    phylogeny_df_pl = pl.from_pandas(phylogeny_df)

    stratified_result_pl = (
        alifestd_downsample_tips_lineage_stratified_polars(
            phylogeny_df_pl, n_tips=n_tips, seed=1
        )
        .lazy()
        .collect()
    )
    stratified_result_pd = stratified_result_pl.to_pandas()
    stratified_bl = alifestd_sum_origin_time_deltas_asexual(
        stratified_result_pd
    )

    rng = np.random.default_rng(42)
    leaf_ids = phylogeny_df.loc[
        ~phylogeny_df["id"].isin(phylogeny_df["ancestor_id"]),
        "id",
    ].values
    random_bls = []
    for _ in range(20):
        chosen = rng.choice(leaf_ids, size=n_tips, replace=False)
        keep = set(chosen)
        for leaf_id in chosen:
            cur = leaf_id
            while cur not in keep or cur == leaf_id:
                keep.add(cur)
                parent = phylogeny_df.loc[
                    phylogeny_df["id"] == cur, "ancestor_id"
                ].values[0]
                if parent == cur:
                    break
                cur = parent
        random_sub = phylogeny_df[phylogeny_df["id"].isin(keep)].copy()
        random_bls.append(alifestd_sum_origin_time_deltas_asexual(random_sub))

    mean_random_bl = np.mean(random_bls)
    assert stratified_bl < mean_random_bl, (
        f"Stratified branch length {stratified_bl} should be less "
        f"than mean random {mean_random_bl}"
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
@pytest.mark.parametrize("n_tips_per_stratum", [1, 2])
def test_alifestd_downsample_tips_lineage_stratified_polars_correct_tip_count(
    phylogeny_df: pd.DataFrame,
    n_tips_per_stratum: int,
):
    """Verify correct total tips and tips-per-stratum counts."""
    n_tips = 4 * n_tips_per_stratum
    phylogeny_df_pl = pl.from_pandas(phylogeny_df)

    result = (
        alifestd_downsample_tips_lineage_stratified_polars(
            phylogeny_df_pl,
            n_tips=n_tips,
            seed=1,
            n_tips_per_stratum=n_tips_per_stratum,
        )
        .lazy()
        .collect()
    )

    result_leaf_count = _count_tips_polars(result)
    # Number of retained tips is min(n_tips, unique_strata * per_stratum)
    assert result_leaf_count <= n_tips
    assert result_leaf_count >= 1
