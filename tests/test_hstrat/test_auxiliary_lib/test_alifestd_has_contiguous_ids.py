import os

import pandas as pd
import pytest

from hstrat._auxiliary_lib import alifestd_has_contiguous_ids

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(
            f"{assets_path}/example-standard-toy-sexual-phylogeny.csv"
        ),
        pd.read_csv(
            f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
        ),
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv")[-1:0],
        pd.read_csv(
            f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
        )[0:1],
    ],
)
def test_alifestd_has_contiguous_ids_true(phylogeny_df):
    phylogeny_df_ = phylogeny_df.copy()
    assert alifestd_has_contiguous_ids(phylogeny_df)
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
def test_alifestd_has_contiguous_ids_false(phylogeny_df):
    phylogeny_df_ = phylogeny_df.copy()
    assert not alifestd_has_contiguous_ids(phylogeny_df)
    # check for side effects
    assert phylogeny_df.equals(phylogeny_df_)
