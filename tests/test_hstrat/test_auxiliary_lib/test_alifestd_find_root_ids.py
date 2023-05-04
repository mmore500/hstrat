import numpy as np
import pandas as pd

from hstrat._auxiliary_lib import alifestd_find_root_ids


def test_alifestd_find_root_ids_returns_expected_output_with_single_root():
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "ancestor_list": ["[none]", "1", "2"],
        }
    )
    expected_output = np.array([1])
    for df in phylogeny_df, phylogeny_df.sample(frac=1):
        output = alifestd_find_root_ids(df)
        assert np.array_equal(output, expected_output)


def test_alifestd_find_root_ids_returns_expected_output_with_multiple_roots():
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4],
            "ancestor_list": ["[none]", "[none]", "1", "2"],
        }
    )
    expected_output = np.array([1, 2])
    for df in phylogeny_df, phylogeny_df.sample(frac=1):
        output = alifestd_find_root_ids(df)
        assert np.array_equal(output, expected_output)


def test_alifestd_find_root_ids_does_not_mutate_input_dataframe():
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "ancestor_list": ["[none]", "1", "2"],
        }
    )
    input_df = phylogeny_df.copy()
    alifestd_find_root_ids(input_df)
    assert phylogeny_df.equals(input_df)
