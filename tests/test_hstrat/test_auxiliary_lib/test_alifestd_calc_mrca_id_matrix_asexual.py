import itertools as it
import os

import numpy as np
import pandas as pd
import pytest
from tqdm import tqdm

from hstrat._auxiliary_lib import (
    alifestd_calc_mrca_id_matrix_asexual,
    alifestd_find_mrca_id_asexual,
    alifestd_is_chronologically_ordered,
    alifestd_to_working_format,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


def make_expected(phylogeny_df: pd.DataFrame) -> np.ndarray:
    n = len(phylogeny_df)
    result = np.zeros((n, n), dtype=np.uint64)
    if n == 0:
        return result

    for (i, id1), (j, id2) in tqdm(
        it.product(enumerate(phylogeny_df["id"]), repeat=2),
    ):
        result[i, j] = alifestd_find_mrca_id_asexual(
            phylogeny_df,
            (id1, id2),
        )

    return result


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
@pytest.mark.parametrize(
    "mutate",
    [True, False],
)
def test_big1(phylogeny_df: pd.DataFrame, mutate: bool):
    assert alifestd_is_chronologically_ordered(phylogeny_df)
    phylogeny_df = alifestd_to_working_format(phylogeny_df)
    original_df = phylogeny_df.copy()

    expected = make_expected(phylogeny_df)
    actual = alifestd_calc_mrca_id_matrix_asexual(phylogeny_df, mutate=mutate)

    np.testing.assert_array_equal(expected, actual)
    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple1(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_list": ["[None]", "[0]", "[1]", "[0]"],
        }
    )
    original_df = phylogeny_df.copy()

    expected = np.array(
        [
            [0, 0, 0, 0],
            [0, 1, 1, 0],
            [0, 1, 2, 0],
            [0, 0, 0, 3],
        ],
        dtype=np.uint64,
    )
    res = alifestd_calc_mrca_id_matrix_asexual(phylogeny_df, mutate=mutate)
    np.testing.assert_array_equal(res, expected)

    if not mutate:
        assert original_df.equals(phylogeny_df)
