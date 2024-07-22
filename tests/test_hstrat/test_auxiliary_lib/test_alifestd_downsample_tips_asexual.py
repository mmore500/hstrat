import os

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_aggregate_phylogenies,
    alifestd_count_leaf_nodes,
    alifestd_downsample_tips_asexual,
    alifestd_prune_extinct_lineages_asexual,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


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
@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize("seed", [1, 42])
def test_alifestd_downsample_tips_asexual(
    phylogeny_df, n_downsample, mutate, seed
):
    original_df = phylogeny_df.copy()

    result_df = alifestd_downsample_tips_asexual(
        phylogeny_df, n_downsample, mutate, seed
    )

    assert len(result_df) <= len(original_df)
    assert "extant" not in result_df.columns

    if not mutate:
        pd.testing.assert_frame_equal(phylogeny_df, original_df)

    assert all(result_df["id"].isin(original_df["id"]))
    assert alifestd_count_leaf_nodes(result_df) == min(
        alifestd_count_leaf_nodes(original_df), n_downsample
    )


@pytest.mark.parametrize("n_downsample", [0, 1])
def test_alifestd_downsample_tips_asexual_with_zero_tips(n_downsample):
    phylogeny_df = pd.DataFrame({"id": [], "parent_id": [], "ancestor_id": []})

    result_df = alifestd_downsample_tips_asexual(phylogeny_df, n_downsample)

    assert result_df.empty


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
def test_prune_tips_vs_downsample(phylogeny_df, n_downsample, seed):
    original_df = phylogeny_df.copy()

    downsampled_df = alifestd_downsample_tips_asexual(
        phylogeny_df, n_downsample, seed=seed
    )

    tips_to_keep = downsampled_df["id"].tolist()
    original_df["extant"] = original_df["id"].isin(tips_to_keep)

    pruned_df = alifestd_prune_extinct_lineages_asexual(
        original_df, mutate=True
    ).drop(columns=["extant"])

    pd.testing.assert_frame_equal(pruned_df, downsampled_df)
