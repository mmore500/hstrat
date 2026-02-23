import os
import typing

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_aggregate_phylogenies,
    alifestd_count_leaf_nodes,
    alifestd_downsample_tips_lineage_stratification_asexual,
    alifestd_to_working_format,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        ),
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        ),
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
        ),
    ],
)
@pytest.mark.parametrize("n_tips", [None, 1, 5, 10])
@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize("seed", [1, 42])
def test_alifestd_downsample_tips_lineage_stratification_asexual(
    phylogeny_df: pd.DataFrame,
    n_tips: typing.Optional[int],
    mutate: bool,
    seed: int,
):
    original_df = phylogeny_df.copy()

    result_df = alifestd_downsample_tips_lineage_stratification_asexual(
        phylogeny_df, n_tips, mutate=mutate, seed=seed
    )

    assert len(result_df) <= len(original_df)
    assert "extant" not in result_df.columns

    if not mutate:
        pd.testing.assert_frame_equal(phylogeny_df, original_df)

    assert all(result_df["id"].isin(original_df["id"]))


@pytest.mark.parametrize("n_tips", [None, 1])
def test_alifestd_downsample_tips_lineage_stratification_asexual_empty(
    n_tips: typing.Optional[int],
):
    phylogeny_df = pd.DataFrame(
        {"id": [], "parent_id": [], "ancestor_id": [], "origin_time": []}
    )

    result_df = alifestd_downsample_tips_lineage_stratification_asexual(
        phylogeny_df, n_tips
    )

    assert result_df.empty


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        ),
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        ),
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
        ),
    ],
)
@pytest.mark.parametrize("seed", [1, 42])
def test_alifestd_downsample_tips_lineage_stratification_asexual_seed_reproducibility(
    phylogeny_df: pd.DataFrame, seed: int
):
    result1 = alifestd_downsample_tips_lineage_stratification_asexual(
        phylogeny_df, 5, seed=seed
    )
    result2 = alifestd_downsample_tips_lineage_stratification_asexual(
        phylogeny_df, 5, seed=seed
    )

    pd.testing.assert_frame_equal(result1, result2)


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        ),
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        ),
    ],
)
def test_alifestd_downsample_tips_lineage_stratification_asexual_none_keeps_all_partitions(
    phylogeny_df: pd.DataFrame,
):
    """With n_tips=None, one tip per distinct partition value is retained."""
    result_df = alifestd_downsample_tips_lineage_stratification_asexual(
        phylogeny_df, seed=1
    )

    assert alifestd_count_leaf_nodes(result_df) >= 1
    assert all(result_df["id"].isin(phylogeny_df["id"]))


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        ),
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        ),
    ],
)
def test_alifestd_downsample_tips_lineage_stratification_asexual_large_n(
    phylogeny_df: pd.DataFrame,
):
    """n_tips larger than distinct values should match n_tips=None."""
    result_none = alifestd_downsample_tips_lineage_stratification_asexual(
        phylogeny_df, seed=1
    )
    result_large = alifestd_downsample_tips_lineage_stratification_asexual(
        phylogeny_df, 100000000, seed=1
    )

    assert alifestd_count_leaf_nodes(
        result_large
    ) == alifestd_count_leaf_nodes(result_none)


def test_alifestd_downsample_tips_lineage_stratification_asexual_missing_criterion():
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1],
            "ancestor_list": ["[none]", "[0]"],
            "origin_time": [0.0, 1.0],
        }
    )

    with pytest.raises(ValueError, match="criterion column"):
        alifestd_downsample_tips_lineage_stratification_asexual(
            phylogeny_df, criterion_delta="nonexistent"
        )

    with pytest.raises(ValueError, match="criterion column"):
        alifestd_downsample_tips_lineage_stratification_asexual(
            phylogeny_df, criterion_stratification="nonexistent"
        )


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        ),
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        ),
    ],
)
def test_alifestd_downsample_tips_lineage_stratification_asexual_custom_criterion(
    phylogeny_df: pd.DataFrame,
):
    result_df = alifestd_downsample_tips_lineage_stratification_asexual(
        phylogeny_df,
        5,
        seed=1,
        criterion_delta="origin_time",
        criterion_stratification="origin_time",
        criterion_target="origin_time",
    )

    assert alifestd_count_leaf_nodes(result_df) >= 1
    assert all(result_df["id"].isin(phylogeny_df["id"]))


def test_alifestd_downsample_tips_lineage_stratification_asexual_multi_tree():
    """Test with aggregated phylogenies (multiple trees)."""
    df1 = alifestd_to_working_format(
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
    )
    df2 = alifestd_to_working_format(
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
    )
    phylogeny_df = alifestd_aggregate_phylogenies([df1, df2])

    result_df = alifestd_downsample_tips_lineage_stratification_asexual(
        phylogeny_df, 5, seed=1
    )

    assert len(result_df) <= len(phylogeny_df)
    assert all(result_df["id"].isin(phylogeny_df["id"]))


def test_alifestd_downsample_tips_lineage_stratification_asexual_no_temp_cols():
    """Ensure no internal temporary columns leak into the output."""
    phylogeny_df = alifestd_to_working_format(
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
    )

    result_df = alifestd_downsample_tips_lineage_stratification_asexual(
        phylogeny_df, 5, seed=1
    )

    for col in result_df.columns:
        assert not col.startswith("_alifestd_downsample")


def test_alifestd_downsample_tips_lineage_stratification_asexual_simple():
    """Test a simple hand-crafted tree.

    Tree structure:
        0 (root, origin_time=0)
        +-- 1 (origin_time=1)
        |   +-- 3 (leaf, origin_time=3)
        |   +-- 4 (leaf, origin_time=4)
        +-- 2 (leaf, origin_time=2)

    With criterion_stratification=origin_time and n_tips=None,
    each unique origin_time among leaves forms its own group.
    Leaves are at origin_time 2, 3, 4 => 3 groups => 3 leaves.
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_list": ["[none]", "[0]", "[0]", "[1]", "[1]"],
            "origin_time": [0.0, 1.0, 2.0, 3.0, 4.0],
        }
    )

    result_df = alifestd_downsample_tips_lineage_stratification_asexual(
        phylogeny_df, seed=1
    )

    # All 3 leaves have distinct origin_times, so all should be retained
    assert alifestd_count_leaf_nodes(result_df) == 3
    assert 0 in result_df["id"].values  # root must be present


def test_alifestd_downsample_tips_lineage_stratification_asexual_n_tips_coarsening():
    """Test that n_tips coarsens partition values via rank + integer division.

    Tree structure:
        0 (root, origin_time=0)
        +-- 1 (origin_time=1)
        |   +-- 3 (leaf, origin_time=3)
        |   +-- 4 (leaf, origin_time=4)
        +-- 2 (leaf, origin_time=2)

    Leaves at origin_time 2, 3, 4 (3 distinct partitions).
    - n_tips=3: ranks [0,1,2], groups [0*3//3, 1*3//3, 2*3//3]=[0,1,2]
      => 3 groups => 3 leaves
    - n_tips=2: ranks [0,1,2], groups [0*2//3, 1*2//3, 2*2//3]=[0,0,1]
      => 2 groups => 2 leaves
    - n_tips=1: ranks [0,1,2], groups [0*1//3, 1*1//3, 2*1//3]=[0,0,0]
      => 1 group => 1 leaf
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_list": ["[none]", "[0]", "[0]", "[1]", "[1]"],
            "origin_time": [0.0, 1.0, 2.0, 3.0, 4.0],
        }
    )

    result3 = alifestd_downsample_tips_lineage_stratification_asexual(
        phylogeny_df, n_tips=3, seed=1
    )
    assert alifestd_count_leaf_nodes(result3) == 3

    result2 = alifestd_downsample_tips_lineage_stratification_asexual(
        phylogeny_df, n_tips=2, seed=1
    )
    assert alifestd_count_leaf_nodes(result2) == 2

    result1 = alifestd_downsample_tips_lineage_stratification_asexual(
        phylogeny_df, n_tips=1, seed=1
    )
    assert alifestd_count_leaf_nodes(result1) == 1


def test_alifestd_downsample_tips_lineage_stratification_asexual_shared_partition():
    """Test where multiple leaves share the same partition value.

    Tree structure:
        0 (root, origin_time=0)
        +-- 1 (origin_time=1)
        |   +-- 3 (leaf, origin_time=2)
        |   +-- 4 (leaf, origin_time=2)
        +-- 2 (leaf, origin_time=2)

    All leaves share origin_time=2, so there is only 1 unique partition.
    Regardless of n_tips, only 1 group is formed => 1 leaf retained.
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_list": ["[none]", "[0]", "[0]", "[1]", "[1]"],
            "origin_time": [0.0, 1.0, 2.0, 2.0, 2.0],
        }
    )

    result_none = alifestd_downsample_tips_lineage_stratification_asexual(
        phylogeny_df, seed=1
    )
    assert alifestd_count_leaf_nodes(result_none) == 1

    result_big = alifestd_downsample_tips_lineage_stratification_asexual(
        phylogeny_df, n_tips=100, seed=1
    )
    assert alifestd_count_leaf_nodes(result_big) == 1
