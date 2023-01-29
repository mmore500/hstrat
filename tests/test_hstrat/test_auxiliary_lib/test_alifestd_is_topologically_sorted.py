import itertools as it
import os
import random

import alifedata_phyloinformatics_convert as apc
import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_is_topologically_sorted,
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
def test_alifestd_is_topologically_sorted_true(phylogeny_df):
    phylogeny_df.sort_values("id", ascending=True, inplace=True)

    phylogeny_df_ = phylogeny_df.copy()
    assert alifestd_is_topologically_sorted(phylogeny_df)

    # check for side effects
    assert phylogeny_df.equals(phylogeny_df_)


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
def test_alifestd_is_topologically_sorted_false(phylogeny_df):
    phylogeny_df.sort_values("id", ascending=False, inplace=True)
    phylogeny_df.set_index("id", drop=False, inplace=True)

    phylogeny_df_ = phylogeny_df.copy()
    assert not alifestd_is_topologically_sorted(phylogeny_df)

    # check for side effects
    assert phylogeny_df.equals(phylogeny_df_)

    # reverse dataframe
    phylogeny_df = phylogeny_df.iloc[::-1]
    assert alifestd_is_topologically_sorted(phylogeny_df)

    # one-by-one transpositions
    for idx, row in phylogeny_df.iterrows():
        for ancestor_id in alifestd_parse_ancestor_ids(row["ancestor_list"]):
            phylogeny_df_ = swap_rows_and_indices(
                phylogeny_df, idx, ancestor_id
            )

            assert not alifestd_is_topologically_sorted(phylogeny_df_)

    # cumulative transpositions in random order
    for idx, row in phylogeny_df.sample(frac=1).iterrows():
        for ancestor_id in alifestd_parse_ancestor_ids(row["ancestor_list"]):
            assert ancestor_id in phylogeny_df_.index
            phylogeny_df = swap_rows_and_indices(
                phylogeny_df, idx, ancestor_id
            )

            assert not alifestd_is_topologically_sorted(phylogeny_df)
