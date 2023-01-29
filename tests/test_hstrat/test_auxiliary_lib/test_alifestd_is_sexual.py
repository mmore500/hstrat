import os

import pandas as pd
import pytest

from hstrat._auxiliary_lib import alifestd_is_sexual

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(
            f"{assets_path}/example-standard-toy-sexual-phylogeny.csv"
        ),
    ],
)
def test_alifestd_is_sexual_true(phylogeny_df):
    phylogeny_df_ = phylogeny_df.copy()
    assert alifestd_is_sexual(phylogeny_df)
    assert phylogeny_df.equals(phylogeny_df_)


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(
            f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
        ),
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
def test_alifestd_is_sexual_false(phylogeny_df):
    phylogeny_df_ = phylogeny_df.copy()
    assert not alifestd_is_sexual(phylogeny_df)
    assert phylogeny_df.equals(phylogeny_df_)
