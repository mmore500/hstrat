import os
import typing

import pandas as pd
import polars as pl
import pytest

from hstrat._auxiliary_lib import (
    alifestd_aggregate_phylogenies,
    alifestd_downsample_tips_asexual,
    alifestd_to_working_format,
)
from hstrat._auxiliary_lib._alifestd_assign_contiguous_ids_polars import (
    alifestd_assign_contiguous_ids_polars,
)
from hstrat._auxiliary_lib._alifestd_downsample_tips_polars import (
    alifestd_downsample_tips_polars,
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
            alifestd_aggregate_phylogenies(
                [
                    pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
                    pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
                ]
            )
        ),
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_tournamentselection.csv")
        ),
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
    assert result_num_tips == min(original_num_tips, n_downsample)


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
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv")
        ),
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv")
        ),
        alifestd_to_working_format(
            alifestd_aggregate_phylogenies(
                [
                    pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
                    pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
                ]
            )
        ),
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_tournamentselection.csv")
        ),
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
    phylogeny_df_pl = apply(pl.from_pandas(phylogeny_df))

    alifestd_downsample_tips_asexual(
        phylogeny_df,
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

    result_num_tips = (
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
    assert result_num_tips == min(n_downsample, original_num_tips)
    assert set(result_pl["id"].to_list()).issubset(
        set(phylogeny_df_pl.lazy().collect()["id"].to_list())
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
def test_alifestd_downsample_tips_polars_deterministic(
    phylogeny_df: pd.DataFrame,
    seed: int,
    apply: typing.Callable,
):
    """Verify same seed produces same result."""
    phylogeny_df_pl = apply(pl.from_pandas(phylogeny_df))

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
