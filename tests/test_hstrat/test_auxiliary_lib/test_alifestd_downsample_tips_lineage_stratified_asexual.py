import os
import typing

import numpy as np
import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_aggregate_phylogenies,
    alifestd_count_leaf_nodes,
    alifestd_downsample_tips_lineage_stratified_asexual,
    alifestd_sum_origin_time_deltas_asexual,
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
def test_alifestd_downsample_tips_lineage_stratified_asexual(
    phylogeny_df: pd.DataFrame,
    n_tips: typing.Optional[int],
    mutate: bool,
    seed: int,
):
    original_df = phylogeny_df.copy()

    result_df = alifestd_downsample_tips_lineage_stratified_asexual(
        phylogeny_df, n_tips, mutate=mutate, seed=seed
    )

    assert len(result_df) <= len(original_df)
    assert "extant" not in result_df.columns

    if not mutate:
        pd.testing.assert_frame_equal(phylogeny_df, original_df)

    assert all(result_df["id"].isin(original_df["id"]))


@pytest.mark.parametrize("n_tips", [None, 1])
def test_alifestd_downsample_tips_lineage_stratified_asexual_empty(
    n_tips: typing.Optional[int],
):
    phylogeny_df = pd.DataFrame(
        {"id": [], "parent_id": [], "ancestor_id": [], "origin_time": []}
    )

    result_df = alifestd_downsample_tips_lineage_stratified_asexual(
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
def test_alifestd_downsample_tips_lineage_stratified_asexual_seed_reproducibility(
    phylogeny_df: pd.DataFrame, seed: int
):
    result1 = alifestd_downsample_tips_lineage_stratified_asexual(
        phylogeny_df, 5, seed=seed
    )
    result2 = alifestd_downsample_tips_lineage_stratified_asexual(
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
def test_alifestd_downsample_tips_lineage_stratified_asexual_none_keeps_all_strata(
    phylogeny_df: pd.DataFrame,
):
    """With n_tips=None, one tip per distinct stratified value is retained."""
    result_df = alifestd_downsample_tips_lineage_stratified_asexual(
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
def test_alifestd_downsample_tips_lineage_stratified_asexual_large_n(
    phylogeny_df: pd.DataFrame,
):
    """n_tips larger than distinct values should match n_tips=None."""
    result_none = alifestd_downsample_tips_lineage_stratified_asexual(
        phylogeny_df, seed=1
    )
    result_large = alifestd_downsample_tips_lineage_stratified_asexual(
        phylogeny_df, 100000000, seed=1
    )

    assert alifestd_count_leaf_nodes(
        result_large
    ) == alifestd_count_leaf_nodes(result_none)


def test_alifestd_downsample_tips_lineage_stratified_asexual_missing_criterion():
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1],
            "ancestor_list": ["[none]", "[0]"],
            "origin_time": [0.0, 1.0],
        }
    )

    with pytest.raises(ValueError, match="criterion column"):
        alifestd_downsample_tips_lineage_stratified_asexual(
            phylogeny_df, criterion_delta="nonexistent"
        )

    with pytest.raises(ValueError, match="criterion column"):
        alifestd_downsample_tips_lineage_stratified_asexual(
            phylogeny_df, criterion_stratify="nonexistent"
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
def test_alifestd_downsample_tips_lineage_stratified_asexual_custom_criterion(
    phylogeny_df: pd.DataFrame,
):
    result_df = alifestd_downsample_tips_lineage_stratified_asexual(
        phylogeny_df,
        5,
        seed=1,
        criterion_delta="origin_time",
        criterion_stratify="origin_time",
        criterion_target="origin_time",
    )

    assert alifestd_count_leaf_nodes(result_df) >= 1
    assert all(result_df["id"].isin(phylogeny_df["id"]))


def test_alifestd_downsample_tips_lineage_stratified_asexual_multi_tree():
    """Test with aggregated phylogenies (multiple trees)."""
    df1 = alifestd_to_working_format(
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
    )
    df2 = alifestd_to_working_format(
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
    )
    phylogeny_df = alifestd_aggregate_phylogenies([df1, df2])

    result_df = alifestd_downsample_tips_lineage_stratified_asexual(
        phylogeny_df, 5, seed=1
    )

    assert len(result_df) <= len(phylogeny_df)
    assert all(result_df["id"].isin(phylogeny_df["id"]))


def test_alifestd_downsample_tips_lineage_stratified_asexual_no_temp_cols():
    """Ensure no internal temporary columns leak into the output."""
    phylogeny_df = alifestd_to_working_format(
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
    )

    result_df = alifestd_downsample_tips_lineage_stratified_asexual(
        phylogeny_df, 5, seed=1
    )

    for col in result_df.columns:
        assert not col.startswith("_alifestd_downsample")


def test_alifestd_downsample_tips_lineage_stratified_asexual_simple():
    """Test a simple hand-crafted tree.

    Tree structure:
        0 (root, origin_time=0)
        +-- 1 (origin_time=1)
        |   +-- 3 (leaf, origin_time=3)
        |   +-- 4 (leaf, origin_time=4)
        +-- 2 (leaf, origin_time=2)

    With criterion_stratify=origin_time and n_tips=None,
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

    result_df = alifestd_downsample_tips_lineage_stratified_asexual(
        phylogeny_df, seed=1
    )

    # All 3 leaves have distinct origin_times, so all should be retained
    assert alifestd_count_leaf_nodes(result_df) == 3
    assert 0 in result_df["id"].values  # root must be present


def test_alifestd_downsample_tips_lineage_stratified_asexual_n_tips_coarsening():
    """Test that n_tips coarsens stratified values via rank + integer division.

    Tree structure:
        0 (root, origin_time=0)
        +-- 1 (origin_time=1)
        |   +-- 3 (leaf, origin_time=3)
        |   +-- 4 (leaf, origin_time=4)
        +-- 2 (leaf, origin_time=2)

    Leaves at origin_time 2, 3, 4 (3 distinct strata).
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

    result3 = alifestd_downsample_tips_lineage_stratified_asexual(
        phylogeny_df, n_tips=3, seed=1
    )
    assert alifestd_count_leaf_nodes(result3) == 3

    result2 = alifestd_downsample_tips_lineage_stratified_asexual(
        phylogeny_df, n_tips=2, seed=1
    )
    assert alifestd_count_leaf_nodes(result2) == 2

    result1 = alifestd_downsample_tips_lineage_stratified_asexual(
        phylogeny_df, n_tips=1, seed=1
    )
    assert alifestd_count_leaf_nodes(result1) == 1


def test_alifestd_downsample_tips_lineage_stratified_asexual_shared_stratum():
    """Test where multiple leaves share the same stratum value.

    Tree structure:
        0 (root, origin_time=0)
        +-- 1 (origin_time=1)
        |   +-- 3 (leaf, origin_time=2)
        |   +-- 4 (leaf, origin_time=2)
        +-- 2 (leaf, origin_time=2)

    All leaves share origin_time=2, so there is only 1 unique stratum.
    Regardless of n_tips, only 1 group is formed => 1 leaf retained.
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_list": ["[none]", "[0]", "[0]", "[1]", "[1]"],
            "origin_time": [0.0, 1.0, 2.0, 2.0, 2.0],
        }
    )

    result_none = alifestd_downsample_tips_lineage_stratified_asexual(
        phylogeny_df, seed=1
    )
    assert alifestd_count_leaf_nodes(result_none) == 1

    result_big = alifestd_downsample_tips_lineage_stratified_asexual(
        phylogeny_df, n_tips=100, seed=1
    )
    assert alifestd_count_leaf_nodes(result_big) == 1


def test_alifestd_downsample_tips_lineage_stratified_asexual_n_tips_per_stratum_validation():
    """n_tips_per_stratum must evenly divide n_tips."""
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_list": ["[none]", "[0]", "[0]", "[1]", "[1]"],
            "origin_time": [0.0, 1.0, 2.0, 3.0, 4.0],
        }
    )

    with pytest.raises(ValueError, match="n_tips_per_stratum"):
        alifestd_downsample_tips_lineage_stratified_asexual(
            phylogeny_df, n_tips=3, seed=1, n_tips_per_stratum=2
        )

    with pytest.raises(ValueError, match="n_tips_per_stratum"):
        alifestd_downsample_tips_lineage_stratified_asexual(
            phylogeny_df, n_tips=5, seed=1, n_tips_per_stratum=3
        )


def test_alifestd_downsample_tips_lineage_stratified_asexual_n_tips_per_stratum_basic():
    """Test n_tips_per_stratum picks correct number of tips per group.

    Tree structure:
        0 (root, ot=0)
        +-- 1 (ot=1)
        |   +-- 3 (leaf, ot=2)
        |   +-- 4 (leaf, ot=2)
        |   +-- 5 (leaf, ot=3)
        |   +-- 6 (leaf, ot=3)
        +-- 2 (leaf, ot=2)

    Strata (origin_time among leaves): {2, 3}.
    With n_tips_per_stratum=2: pick 2 from each stratum.
    Stratum 2 has 3 leaves (2, 3, 4), stratum 3 has 2 leaves (5, 6).
    Result: 2 + 2 = 4 leaves.
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_list": [
                "[none]",
                "[0]",
                "[0]",
                "[1]",
                "[1]",
                "[1]",
                "[1]",
            ],
            "origin_time": [0.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0],
        }
    )

    result = alifestd_downsample_tips_lineage_stratified_asexual(
        phylogeny_df, seed=1, n_tips_per_stratum=2
    )
    assert alifestd_count_leaf_nodes(result) == 4

    result1 = alifestd_downsample_tips_lineage_stratified_asexual(
        phylogeny_df, seed=1, n_tips_per_stratum=1
    )
    assert alifestd_count_leaf_nodes(result1) == 2


def test_alifestd_downsample_tips_lineage_stratified_asexual_n_tips_per_stratum_with_n_tips():
    """Test n_tips_per_stratum combined with n_tips.

    Tree structure:
        0 (root, ot=0)
        +-- 1 (ot=1)
        |   +-- 3 (leaf, ot=2)
        |   +-- 4 (leaf, ot=2)
        |   +-- 5 (leaf, ot=3)
        |   +-- 6 (leaf, ot=3)
        +-- 2 (leaf, ot=2)

    n_tips=4, n_tips_per_stratum=2: 4//2=2 groups.
    2 distinct strata, so 2 groups map naturally => 2 tips per group = 4.
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_list": [
                "[none]",
                "[0]",
                "[0]",
                "[1]",
                "[1]",
                "[1]",
                "[1]",
            ],
            "origin_time": [0.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0],
        }
    )

    result = alifestd_downsample_tips_lineage_stratified_asexual(
        phylogeny_df, n_tips=4, seed=1, n_tips_per_stratum=2
    )
    assert alifestd_count_leaf_nodes(result) == 4


def test_alifestd_downsample_tips_lineage_stratified_asexual_n_tips_per_stratum_no_ranking():
    """With n_tips_per_stratum only (n_tips=None), stratify values are not
    coarsened by ranking --- each distinct value forms its own stratum.

    Construct a tree where ranking would merge strata but n_tips=None
    should keep them separate.
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6, 7, 8],
            "ancestor_list": [
                "[none]",
                "[0]",
                "[0]",
                "[1]",
                "[1]",
                "[2]",
                "[2]",
                "[2]",
                "[2]",
            ],
            "origin_time": [
                0.0,
                1.0,
                1.0,
                10.0,
                10.0,
                20.0,
                20.0,
                30.0,
                30.0,
            ],
        }
    )

    # n_tips=None: 3 distinct leaf strata {10, 20, 30}, pick 1 each = 3
    result = alifestd_downsample_tips_lineage_stratified_asexual(
        phylogeny_df, seed=1, n_tips_per_stratum=1
    )
    assert alifestd_count_leaf_nodes(result) == 3

    # n_tips=None, n_tips_per_stratum=2: 3 strata, pick 2 each = 6
    result2 = alifestd_downsample_tips_lineage_stratified_asexual(
        phylogeny_df, seed=1, n_tips_per_stratum=2
    )
    assert alifestd_count_leaf_nodes(result2) == 6


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
def test_alifestd_downsample_tips_lineage_stratified_asexual_less_branch_length_than_random(
    phylogeny_df: pd.DataFrame,
):
    """Stratified downsampling should pull less total branch length (sum of
    origin_time deltas) than random tip sampling, on asset datasets with a
    spread of origin times.
    """
    n_tips = 5

    stratified_result = alifestd_downsample_tips_lineage_stratified_asexual(
        phylogeny_df, n_tips=n_tips, seed=1
    )
    stratified_bl = alifestd_sum_origin_time_deltas_asexual(stratified_result)

    # Random tip sampling: keep n_tips random leaves and their lineages
    rng = np.random.default_rng(42)
    leaf_ids = phylogeny_df.loc[
        ~phylogeny_df["id"].isin(phylogeny_df["ancestor_id"]),
        "id",
    ].values
    random_bls = []
    for _ in range(20):
        chosen = rng.choice(leaf_ids, size=n_tips, replace=False)
        # Build the set of ancestors for the chosen leaves
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
            pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        ),
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        ),
    ],
)
@pytest.mark.parametrize("n_tips_per_stratum", [1, 2])
def test_alifestd_downsample_tips_lineage_stratified_asexual_correct_tip_count(
    phylogeny_df: pd.DataFrame,
    n_tips_per_stratum: int,
):
    """Verify correct total tips and tips-per-stratum counts."""
    n_tips = 4 * n_tips_per_stratum

    result = alifestd_downsample_tips_lineage_stratified_asexual(
        phylogeny_df,
        n_tips=n_tips,
        seed=1,
        n_tips_per_stratum=n_tips_per_stratum,
    )

    result_leaf_count = alifestd_count_leaf_nodes(result)
    # Number of retained tips is min(n_tips, unique_strata * per_stratum)
    assert result_leaf_count <= n_tips
    assert result_leaf_count >= 1

    # Verify per-stratum: leaf origin_times form strata; each should
    # have at most n_tips_per_stratum leaves.
    result_leaves = result[~result["id"].isin(result["ancestor_id"])]
    strata_counts = result_leaves["origin_time"].value_counts()
    assert all(strata_counts <= n_tips_per_stratum)
