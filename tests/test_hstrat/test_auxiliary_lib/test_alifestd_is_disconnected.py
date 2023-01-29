import os

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_is_disconnected,
    alifestd_parse_ancestor_ids,
    swap_rows_and_indices,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
def test_alifestd_is_disconnected_empty(phylogeny_df):
    phylogeny_df.sort_values("id", ascending=True, inplace=True)

    assert not alifestd_is_disconnected(phylogeny_df.iloc[-1:0, :])


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
def test_alifestd_is_disconnected_singleton(phylogeny_df):
    phylogeny_df.sort_values("id", ascending=True, inplace=True)

    assert not alifestd_is_disconnected(phylogeny_df.iloc[0:1, :])


def test_alifestd_is_disconnected_tworoots():

    phylo1 = pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv")
    phylo1.sort_values("id", ascending=True, inplace=True)

    phylo2 = pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv")
    phylo2.sort_values("id", ascending=True, inplace=True)

    assert alifestd_is_disconnected(
        pd.concat(
            [
                phylo1.iloc[0:1, :],
                phylo2.iloc[0:1, :],
            ]
        )
    )


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
def test_alifestd_is_disconnected_twolineages(phylogeny_df):

    phylogeny_df.sort_values("id", ascending=True, inplace=True)
    phylogeny_df.reset_index(inplace=True)
    max_id = phylogeny_df["id"].max()

    lineage1 = phylogeny_df.copy()
    lineage2 = phylogeny_df.copy()
    lineage2["id"] += max_id
    lineage2["ancestor_list"] = lineage2["ancestor_list"].apply(
        lambda ancestor_list_str: str(
            [
                ancestor_id + max_id
                for ancestor_id in alifestd_parse_ancestor_ids(
                    ancestor_list_str
                )
            ]
        )
    )
    assert alifestd_is_disconnected(
        pd.concat(
            [
                lineage1,
                lineage2,
            ]
        )
    )
    assert alifestd_is_disconnected(
        pd.concat(
            [
                lineage1,
                lineage2,
            ]
        ).sort_index()
    )
    assert alifestd_is_disconnected(
        pd.concat(
            [
                lineage1.iloc[::-1, :],
                lineage2,
            ]
        )
    )
    assert alifestd_is_disconnected(
        pd.concat(
            [
                lineage1.iloc[:10:-1, :],
                lineage2,
                lineage1.iloc[10::-1, :],
            ]
        )
    )
    assert alifestd_is_disconnected(
        pd.concat(
            [
                lineage1.iloc[10::, :],
                lineage2,
                lineage1.iloc[:10:, :],
            ]
        )
    )


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
def test_alifestd_is_disconnected_false(phylogeny_df):
    phylogeny_df.sort_values("id", ascending=False, inplace=True)
    phylogeny_df.set_index("id", drop=False, inplace=True)

    phylogeny_df_ = phylogeny_df.copy()
    assert not alifestd_is_disconnected(phylogeny_df)

    # check for side effects
    assert phylogeny_df.equals(phylogeny_df_)

    # reverse dataframe
    phylogeny_df = phylogeny_df.iloc[::-1]
    assert not alifestd_is_disconnected(phylogeny_df)

    # one-by-one transpositions
    for idx, row in phylogeny_df.iterrows():
        for ancestor_id in alifestd_parse_ancestor_ids(row["ancestor_list"]):
            phylogeny_df_ = swap_rows_and_indices(
                phylogeny_df, idx, ancestor_id
            )

            assert not alifestd_is_disconnected(phylogeny_df_)