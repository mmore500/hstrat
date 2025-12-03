import itertools as it
import os

import numpy as np
import pandas as pd
import pytest
from tqdm import tqdm

from hstrat._auxiliary_lib import (
    alifestd_calc_mrca_id_matrix_asexual,
    alifestd_calc_mrca_id_vector_asexual,
    alifestd_is_chronologically_ordered,
    alifestd_to_working_format,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


def make_actual(
    phylogeny_df: pd.DataFrame,
    mutate: bool,
) -> np.ndarray:
    res = [
        alifestd_calc_mrca_id_vector_asexual(
            phylogeny_df,
            mutate=mutate,
            progress_wrap=tqdm,
            target_id=i,
        )
        for i in tqdm(range(len(phylogeny_df)))
    ]
    if len(res) == 0:
        return np.zeros((0, 0), dtype=np.int64)
    else:
        return np.stack(res, axis=0)


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
    phylogeny_df = phylogeny_df.copy()
    assert alifestd_is_chronologically_ordered(phylogeny_df)
    phylogeny_df = alifestd_to_working_format(phylogeny_df)
    original_df = phylogeny_df.copy()

    actual = make_actual(phylogeny_df.copy(), mutate=mutate)
    expected = alifestd_calc_mrca_id_matrix_asexual(
        phylogeny_df,
    )

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
        dtype=np.int64,
    )
    actual = make_actual(phylogeny_df, mutate=mutate)
    np.testing.assert_array_equal(actual, expected)

    # ensure idempotency
    actual = alifestd_calc_mrca_id_matrix_asexual(phylogeny_df, mutate=mutate)
    np.testing.assert_array_equal(actual, expected)

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.DataFrame(
            {
                "id": [],
                "ancestor_list": [],
            }
        ),
        pd.DataFrame(
            {
                "id": [],
                "ancestor_id": [],
            }
        ),
        pd.DataFrame(
            {
                "id": [0],
                "ancestor_list": ["[None]"],
            }
        ),
        pd.DataFrame(
            {
                "id": [0],
                "ancestor_id": [0],
                "ancestor_list": ["[None]"],
            }
        ),
        pd.DataFrame(
            {
                "id": [0, 1],
                "ancestor_list": ["[None]", "[0]"],
            }
        ),
        pd.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_id": [0, 1, 2],
            }
        ),
        pd.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_id": [0, 0, 0],
                "ancestor_list": ["[None]", "[0]", "[0]"],
            }
        ),
        pd.DataFrame(
            {
                "id": [0, 1, 2],
                "ancestor_list": ["[None]", "[None]", "[1]"],
            }
        ),
        pd.DataFrame(
            {
                "id": [0, 1, 2, 3],
                "ancestor_id": [0, 0, 2, 1],
            }
        ),
        pd.DataFrame(
            {
                "id": [0, 1, 2, 3],
                "ancestor_id": [0, 0, 0, 0],
            }
        ),
        pd.DataFrame(
            {
                "id": [0, 1, 2, 3],
                "ancestor_list": ["[None]", "[0]", "[0]", "[0]"],
            }
        ),
    ],
)
def test_edge_cases(phylogeny_df: pd.DataFrame, mutate: bool):
    phylogeny_df = phylogeny_df.copy()
    original_df = phylogeny_df.copy()

    actual = make_actual(phylogeny_df, mutate=mutate)
    expected = alifestd_calc_mrca_id_matrix_asexual(
        phylogeny_df,
    )
    np.testing.assert_array_equal(actual, expected)

    # ensure idempotency
    actual = make_actual(phylogeny_df, mutate=mutate)
    np.testing.assert_array_equal(actual, expected)

    if not mutate:
        assert original_df.equals(phylogeny_df)
