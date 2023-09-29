import itertools as it
import os

import numpy as np
import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_find_mrca_id_asexual,
    alifestd_is_chronologically_ordered,
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
def test_fuzz(phylogeny_df: pd.DataFrame):
    assert alifestd_is_chronologically_ordered(phylogeny_df)

    for ids in it.islice(
        it.product(phylogeny_df["id"], phylogeny_df["id"]), 2
    ):
        res = alifestd_find_mrca_id_asexual(phylogeny_df, ids)
        assert res >= phylogeny_df["id"].min()
        assert all(res <= np.array(ids))

    for id_ in it.islice(reversed(phylogeny_df["id"]), 2):
        res = alifestd_find_mrca_id_asexual(phylogeny_df, [id_] * 3)
        assert res == id_


@pytest.mark.parametrize("mutate", [True, False])
def test_simple1(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 4],
            "ancestor_list": ["[None]", "[0]", "[1]", "[0]"],
        }
    )
    original_df = phylogeny_df.copy()

    res = alifestd_find_mrca_id_asexual(phylogeny_df, (0, 1, 2), mutate=mutate)
    assert res == 0

    res = alifestd_find_mrca_id_asexual(phylogeny_df, (0, 2), mutate=mutate)
    assert res == 0

    res = alifestd_find_mrca_id_asexual(phylogeny_df, (2,), mutate=mutate)
    assert res == 2

    res = alifestd_find_mrca_id_asexual(phylogeny_df, (2, 1), mutate=mutate)
    assert res == 1

    res = alifestd_find_mrca_id_asexual(phylogeny_df, (2, 4), mutate=mutate)
    assert res == 0

    if not mutate:
        assert original_df.equals(phylogeny_df)
