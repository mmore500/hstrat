import os

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_aggregate_phylogenies,
    alifestd_count_leaf_nodes,
    alifestd_downsample_tips_lineage_asexual,
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
@pytest.mark.parametrize("num_tips", [1, 5, 10, 100000000])
@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize("seed", [1, 42])
def test_alifestd_downsample_tips_lineage_asexual(
    phylogeny_df, num_tips, mutate, seed
):
    original_df = phylogeny_df.copy()

    result_df = alifestd_downsample_tips_lineage_asexual(
        phylogeny_df, num_tips, mutate=mutate, seed=seed
    )

    assert len(result_df) <= len(original_df)
    assert "extant" not in result_df.columns

    if not mutate:
        pd.testing.assert_frame_equal(phylogeny_df, original_df)

    assert all(result_df["id"].isin(original_df["id"]))
    assert alifestd_count_leaf_nodes(result_df) <= min(
        alifestd_count_leaf_nodes(original_df), num_tips
    )


@pytest.mark.parametrize("num_tips", [0, 1])
def test_alifestd_downsample_tips_lineage_asexual_empty(num_tips):
    phylogeny_df = pd.DataFrame(
        {"id": [], "parent_id": [], "ancestor_id": [], "origin_time": []}
    )

    result_df = alifestd_downsample_tips_lineage_asexual(
        phylogeny_df, num_tips
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
def test_alifestd_downsample_tips_lineage_asexual_seed_reproducibility(
    phylogeny_df, seed
):
    result1 = alifestd_downsample_tips_lineage_asexual(
        phylogeny_df, 5, seed=seed
    )
    result2 = alifestd_downsample_tips_lineage_asexual(
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
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
        ),
    ],
)
def test_alifestd_downsample_tips_lineage_asexual_single_tip(phylogeny_df):
    result_df = alifestd_downsample_tips_lineage_asexual(
        phylogeny_df, 1, seed=1
    )

    assert alifestd_count_leaf_nodes(result_df) == 1


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
def test_alifestd_downsample_tips_lineage_asexual_all_tips(phylogeny_df):
    original_leaf_count = alifestd_count_leaf_nodes(phylogeny_df)

    result_df = alifestd_downsample_tips_lineage_asexual(
        phylogeny_df, original_leaf_count + 100, seed=1
    )

    assert alifestd_count_leaf_nodes(result_df) == original_leaf_count


def test_alifestd_downsample_tips_lineage_asexual_missing_criterion():
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1],
            "ancestor_list": ["[none]", "[0]"],
            "origin_time": [0.0, 1.0],
        }
    )

    with pytest.raises(ValueError, match="criterion column"):
        alifestd_downsample_tips_lineage_asexual(
            phylogeny_df, 1, criterion_delta="nonexistent"
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
def test_alifestd_downsample_tips_lineage_asexual_custom_criterion(
    phylogeny_df,
):
    result_df = alifestd_downsample_tips_lineage_asexual(
        phylogeny_df,
        5,
        seed=1,
        criterion_delta="origin_time",
        criterion_target="origin_time",
    )

    assert alifestd_count_leaf_nodes(result_df) == 5
    assert all(result_df["id"].isin(phylogeny_df["id"]))


def test_alifestd_downsample_tips_lineage_asexual_multi_tree():
    """Test with aggregated phylogenies (multiple trees)."""
    df1 = alifestd_to_working_format(
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
    )
    df2 = alifestd_to_working_format(
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
    )
    phylogeny_df = alifestd_aggregate_phylogenies([df1, df2])

    result_df = alifestd_downsample_tips_lineage_asexual(
        phylogeny_df, 5, seed=1
    )

    assert len(result_df) <= len(phylogeny_df)
    assert alifestd_count_leaf_nodes(result_df) <= 5
    assert all(result_df["id"].isin(phylogeny_df["id"]))


def test_alifestd_downsample_tips_lineage_asexual_no_temp_cols():
    """Ensure no internal temporary columns leak into the output."""
    phylogeny_df = alifestd_to_working_format(
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
    )

    result_df = alifestd_downsample_tips_lineage_asexual(
        phylogeny_df, 5, seed=1
    )

    for col in result_df.columns:
        assert not col.startswith("_alifestd_downsample")
