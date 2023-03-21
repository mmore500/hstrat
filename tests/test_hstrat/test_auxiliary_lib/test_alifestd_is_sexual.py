import os

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_is_sexual,
    alifestd_to_working_format,
    alifestd_try_add_ancestor_id_col,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(
            f"{assets_path}/example-standard-toy-sexual-phylogeny.csv"
        ),
    ],
)
@pytest.mark.parametrize(
    "apply",
    [
        alifestd_to_working_format,
        alifestd_try_add_ancestor_id_col,
        lambda x: x,
    ],
)
def test_alifestd_is_sexual_true(phylogeny_df, apply):
    phylogeny_df = apply(phylogeny_df)
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
        pd.DataFrame({"id": [], "ancestor_list": []}),
    ],
)
@pytest.mark.parametrize(
    "apply",
    [
        alifestd_to_working_format,
        alifestd_try_add_ancestor_id_col,
        lambda x: x,
    ],
)
def test_alifestd_is_sexual_false(phylogeny_df, apply):
    phylogeny_df = apply(phylogeny_df)
    phylogeny_df_ = phylogeny_df.copy()
    assert not alifestd_is_sexual(phylogeny_df)
    assert phylogeny_df.equals(phylogeny_df_)
