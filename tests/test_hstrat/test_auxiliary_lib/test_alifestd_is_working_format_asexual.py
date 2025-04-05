import os

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_aggregate_phylogenies,
    alifestd_is_asexual,
    alifestd_is_working_format_asexual,
    alifestd_to_working_format,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(
            f"{assets_path}/example-standard-toy-sexual-phylogeny.csv"
        ),
        alifestd_aggregate_phylogenies(
            [
                pd.read_csv(
                    f"{assets_path}/example-standard-toy-sexual-phylogeny.csv"
                ),
                pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
            ]
        ),
        pd.read_csv(
            f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
        ),
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
def test_alifestd_is_working_format(phylogeny_df):
    phylogeny_df_ = phylogeny_df.copy()
    working_df = alifestd_to_working_format(phylogeny_df)

    if alifestd_is_working_format_asexual(phylogeny_df):
        assert working_df.equals(phylogeny_df)
    elif alifestd_is_asexual(phylogeny_df):
        assert not working_df.equals(phylogeny_df)

    if alifestd_is_asexual(phylogeny_df):
        assert alifestd_is_working_format_asexual(working_df)
    else:
        assert not alifestd_is_working_format_asexual(working_df)

    # check for side effects
    assert phylogeny_df.equals(phylogeny_df_)
