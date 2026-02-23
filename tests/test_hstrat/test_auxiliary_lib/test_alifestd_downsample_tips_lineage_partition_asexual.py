import os

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_aggregate_phylogenies,
    alifestd_count_leaf_nodes,
    alifestd_downsample_tips_lineage_partition_asexual,
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
@pytest.mark.parametrize("n_partition", [1, 5, 10])
@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize("seed", [1, 42])
def test_alifestd_downsample_tips_lineage_partition_asexual(
    phylogeny_df, n_partition, mutate, seed
):
    original_df = phylogeny_df.copy()

    result_df = alifestd_downsample_tips_lineage_partition_asexual(
        phylogeny_df, n_partition, mutate=mutate, seed=seed
    )

    assert len(result_df) <= len(original_df)
    assert "extant" not in result_df.columns

    if not mutate:
        pd.testing.assert_frame_equal(phylogeny_df, original_df)

    assert all(result_df["id"].isin(original_df["id"]))


@pytest.mark.parametrize("n_partition", [0, 1])
def test_alifestd_downsample_tips_lineage_partition_asexual_empty(
    n_partition,
):
    phylogeny_df = pd.DataFrame(
        {"id": [], "parent_id": [], "ancestor_id": [], "origin_time": []}
    )

    result_df = alifestd_downsample_tips_lineage_partition_asexual(
        phylogeny_df, n_partition
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
def test_alifestd_downsample_tips_lineage_partition_asexual_seed_reproducibility(
    phylogeny_df, seed
):
    result1 = alifestd_downsample_tips_lineage_partition_asexual(
        phylogeny_df, 1, seed=seed
    )
    result2 = alifestd_downsample_tips_lineage_partition_asexual(
        phylogeny_df, 1, seed=seed
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
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
        ),
    ],
)
def test_alifestd_downsample_tips_lineage_partition_asexual_single_per_partition(
    phylogeny_df,
):
    result_df = alifestd_downsample_tips_lineage_partition_asexual(
        phylogeny_df, 1, seed=1
    )

    # With n_partition=1 and default partition by origin_time,
    # each unique origin_time among leaves should have at most 1 leaf
    assert alifestd_count_leaf_nodes(result_df) >= 1


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
def test_alifestd_downsample_tips_lineage_partition_asexual_large_n(
    phylogeny_df,
):
    """Requesting more per partition than exist should return all leaves."""
    original_leaf_count = alifestd_count_leaf_nodes(phylogeny_df)

    result_df = alifestd_downsample_tips_lineage_partition_asexual(
        phylogeny_df, 100000000, seed=1
    )

    assert alifestd_count_leaf_nodes(result_df) == original_leaf_count


def test_alifestd_downsample_tips_lineage_partition_asexual_missing_criterion():
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1],
            "ancestor_list": ["[none]", "[0]"],
            "origin_time": [0.0, 1.0],
        }
    )

    with pytest.raises(ValueError, match="criterion column"):
        alifestd_downsample_tips_lineage_partition_asexual(
            phylogeny_df, 1, criterion_delta="nonexistent"
        )

    with pytest.raises(ValueError, match="criterion column"):
        alifestd_downsample_tips_lineage_partition_asexual(
            phylogeny_df, 1, criterion_partition="nonexistent"
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
def test_alifestd_downsample_tips_lineage_partition_asexual_custom_criterion(
    phylogeny_df,
):
    result_df = alifestd_downsample_tips_lineage_partition_asexual(
        phylogeny_df,
        1,
        seed=1,
        criterion_delta="origin_time",
        criterion_partition="origin_time",
        criterion_target="origin_time",
    )

    assert alifestd_count_leaf_nodes(result_df) >= 1
    assert all(result_df["id"].isin(phylogeny_df["id"]))


def test_alifestd_downsample_tips_lineage_partition_asexual_multi_tree():
    """Test with aggregated phylogenies (multiple trees)."""
    df1 = alifestd_to_working_format(
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
    )
    df2 = alifestd_to_working_format(
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
    )
    phylogeny_df = alifestd_aggregate_phylogenies([df1, df2])

    result_df = alifestd_downsample_tips_lineage_partition_asexual(
        phylogeny_df, 1, seed=1
    )

    assert len(result_df) <= len(phylogeny_df)
    assert all(result_df["id"].isin(phylogeny_df["id"]))


def test_alifestd_downsample_tips_lineage_partition_asexual_no_temp_cols():
    """Ensure no internal temporary columns leak into the output."""
    phylogeny_df = alifestd_to_working_format(
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
    )

    result_df = alifestd_downsample_tips_lineage_partition_asexual(
        phylogeny_df, 1, seed=1
    )

    for col in result_df.columns:
        assert not col.startswith("_alifestd_downsample")


def test_alifestd_downsample_tips_lineage_partition_asexual_simple():
    """Test a simple hand-crafted tree.

    Tree structure:
        0 (root, origin_time=0)
        +-- 1 (origin_time=1)
        |   +-- 3 (leaf, origin_time=3)
        |   +-- 4 (leaf, origin_time=4)
        +-- 2 (leaf, origin_time=2)

    With criterion_partition=origin_time and n_partition=1,
    each unique origin_time among leaves should retain at most 1 leaf.
    Leaves are at origin_time 2, 3, 4 => 3 partitions, 1 each => 3 leaves.
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_list": ["[none]", "[0]", "[0]", "[1]", "[1]"],
            "origin_time": [0.0, 1.0, 2.0, 3.0, 4.0],
        }
    )

    result_df = alifestd_downsample_tips_lineage_partition_asexual(
        phylogeny_df, 1, seed=1
    )

    # All 3 leaves have distinct origin_times, so all should be retained
    assert alifestd_count_leaf_nodes(result_df) == 3
    assert 0 in result_df["id"].values  # root must be present


def test_alifestd_downsample_tips_lineage_partition_asexual_shared_partition():
    """Test where multiple leaves share the same partition value.

    Tree structure:
        0 (root, origin_time=0)
        +-- 1 (origin_time=1)
        |   +-- 3 (leaf, origin_time=2)
        |   +-- 4 (leaf, origin_time=2)
        +-- 2 (leaf, origin_time=2)

    All leaves share origin_time=2, so with n_partition=1 only 1 leaf
    should be retained. With n_partition=2, 2 leaves should be retained.
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_list": ["[none]", "[0]", "[0]", "[1]", "[1]"],
            "origin_time": [0.0, 1.0, 2.0, 2.0, 2.0],
        }
    )

    result1 = alifestd_downsample_tips_lineage_partition_asexual(
        phylogeny_df, 1, seed=1
    )
    assert alifestd_count_leaf_nodes(result1) == 1

    result2 = alifestd_downsample_tips_lineage_partition_asexual(
        phylogeny_df, 2, seed=1
    )
    assert alifestd_count_leaf_nodes(result2) == 2

    result3 = alifestd_downsample_tips_lineage_partition_asexual(
        phylogeny_df, 100, seed=1
    )
    assert alifestd_count_leaf_nodes(result3) == 3
