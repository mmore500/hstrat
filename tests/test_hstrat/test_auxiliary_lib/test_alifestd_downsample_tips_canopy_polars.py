import os

import pandas as pd
import polars as pl
import pytest

from hstrat._auxiliary_lib import (
    alifestd_aggregate_phylogenies,
    alifestd_find_leaf_ids,
    alifestd_to_working_format,
)
from hstrat._auxiliary_lib._alifestd_downsample_tips_canopy_asexual import (
    alifestd_downsample_tips_canopy_asexual,
)
from hstrat._auxiliary_lib._alifestd_downsample_tips_canopy_polars import (
    alifestd_downsample_tips_canopy_polars,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


def _count_leaf_nodes_polars(phylogeny_df: pl.DataFrame) -> int:
    """Count leaf nodes in a polars dataframe (works with any ids)."""
    all_ids = set(phylogeny_df["id"].to_list())
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
@pytest.mark.parametrize("num_tips", [1, 5, 10, 100000000])
def test_alifestd_downsample_tips_canopy_polars(
    phylogeny_df: pd.DataFrame,
    num_tips: int,
):
    phylogeny_df_pl = pl.from_pandas(phylogeny_df)

    original_len = len(phylogeny_df_pl)
    original_num_tips = _count_leaf_nodes_polars(phylogeny_df_pl)

    result_df = alifestd_downsample_tips_canopy_polars(
        phylogeny_df_pl,
        num_tips,
        criterion="id",
    )

    assert len(result_df) <= original_len
    assert "extant" not in result_df.columns
    assert set(result_df["id"].to_list()).issubset(
        set(phylogeny_df_pl["id"].to_list())
    )
    assert _count_leaf_nodes_polars(result_df) == min(
        original_num_tips, num_tips
    )


@pytest.mark.parametrize("num_tips", [0, 1])
def test_alifestd_downsample_tips_canopy_polars_empty(num_tips: int):
    phylogeny_df = pl.DataFrame(
        {"id": [], "ancestor_id": []},
        schema={"id": pl.Int64, "ancestor_id": pl.Int64},
    )

    result_df = alifestd_downsample_tips_canopy_polars(
        phylogeny_df, num_tips, criterion="id"
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
@pytest.mark.parametrize("num_tips", [1, 5, 10])
def test_alifestd_downsample_tips_canopy_polars_matches_pandas(
    phylogeny_df: pd.DataFrame,
    num_tips: int,
):
    """Verify polars result matches pandas result for same prepared input."""
    phylogeny_df_pl = pl.from_pandas(phylogeny_df)

    result_pd = alifestd_downsample_tips_canopy_asexual(
        phylogeny_df, num_tips, mutate=False, criterion="id"
    )
    result_pl = alifestd_downsample_tips_canopy_polars(
        phylogeny_df_pl, num_tips, criterion="id"
    )

    assert set(result_pd["id"]) == set(result_pl["id"].to_list())
    assert len(result_pd) == len(result_pl)


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
def test_alifestd_downsample_tips_canopy_polars_retains_highest_ids(
    phylogeny_df: pd.DataFrame,
):
    """Verify that the retained tips are the ones with the highest ids."""
    num_tips = 5
    phylogeny_df_pl = pl.from_pandas(phylogeny_df)
    result_df = alifestd_downsample_tips_canopy_polars(
        phylogeny_df_pl, num_tips, criterion="id"
    )

    original_tips = alifestd_find_leaf_ids(phylogeny_df)
    expected_kept = set(sorted(original_tips)[-num_tips:])

    result_tips_all = set(result_df["id"].to_list())
    # find leaf ids in result: ids that don't appear as ancestor_id of others
    internal_ids = set(
        result_df.filter(pl.col("ancestor_id") != pl.col("id"))
        .select("ancestor_id")
        .to_series()
        .to_list()
    )
    result_tips = result_tips_all - internal_ids
    assert result_tips == expected_kept


def test_alifestd_downsample_tips_canopy_polars_no_ancestor_id():
    df = pl.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[none]", "[0]", "[1]"],
        }
    )
    with pytest.raises(NotImplementedError):
        alifestd_downsample_tips_canopy_polars(df, 1, criterion="id")


def test_alifestd_downsample_tips_canopy_polars_simple():
    """Test a simple hand-crafted tree.

    Tree structure:
        0 (root)
        +-- 1
        |   +-- 3 (leaf)
        |   +-- 4 (leaf)
        +-- 2 (leaf)

    With num_tips=2, keep leaves 3 and 4 (highest ids), result is 0, 1, 3, 4.
    With num_tips=1, keep leaf 4 (highest id), result is 0, 1, 4.
    """
    df = pl.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_id": [0, 0, 0, 1, 1],
            "destruction_time": [float("inf")] * 5,
        }
    )

    result2 = alifestd_downsample_tips_canopy_polars(df, 2, criterion="id")
    assert set(result2["id"].to_list()) == {0, 1, 3, 4}

    result1 = alifestd_downsample_tips_canopy_polars(df, 1, criterion="id")
    assert set(result1["id"].to_list()) == {0, 1, 4}


def test_alifestd_downsample_tips_canopy_polars_all_tips():
    """Requesting more tips than exist should return the full phylogeny."""
    df = pl.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_id": [0, 0, 0, 1, 1],
            "destruction_time": [float("inf")] * 5,
        }
    )

    result = alifestd_downsample_tips_canopy_polars(df, 100000, criterion="id")

    assert len(result) == 5


def test_alifestd_downsample_tips_canopy_polars_tied_criterion():
    """When all leaves share the same criterion value, exactly num_tips
    should still be retained (ties broken arbitrarily)."""
    df = pl.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_id": [0, 0, 0, 1, 1],
            "destruction_time": [float("inf")] * 5,
            "time": [0, 0, 0, 0, 0],
        }
    )
    # leaves are 2, 3, 4 — all have time=0
    for num_tips in (1, 2, 3):
        result = alifestd_downsample_tips_canopy_polars(
            df, num_tips, criterion="time"
        )
        assert _count_leaf_nodes_polars(result) == num_tips


def test_alifestd_downsample_tips_canopy_polars_missing_criterion():
    """Verify ValueError when criterion column is missing."""
    df = pl.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_id": [0, 0, 0],
        }
    )

    with pytest.raises(ValueError, match="criterion column"):
        alifestd_downsample_tips_canopy_polars(df, 1, criterion="nonexistent")
