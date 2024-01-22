import numpy as np
import pandas as pd

from hstrat._auxiliary_lib import alifestd_find_root_ids, alifestd_make_empty


def test_no_root():
    assert np.array_equal(
        alifestd_find_root_ids(alifestd_make_empty()),
        np.array([]),
    )


def test_singleton():
    phylogeny_df = pd.DataFrame(
        {
            "id": [0],
            "ancestor_list": ["[none]"],
        }
    )
    assert np.array_equal(alifestd_find_root_ids(phylogeny_df), np.array([0]))


def test_alifestd_find_root_ids_returns_expected_output_with_single_root():
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "ancestor_list": ["[none]", "[1]", "[2]"],
        }
    )
    expected_output = np.array([1])
    output = alifestd_find_root_ids(phylogeny_df)
    assert np.array_equal(output, expected_output)


def test_alifestd_find_root_ids_returns_expected_output_with_multiple_roots():
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4],
            "ancestor_list": ["[none]", "[none]", "[1]", "[2]"],
        }
    )
    expected_output = np.array([1, 2])
    output = alifestd_find_root_ids(phylogeny_df)
    assert np.array_equal(output, expected_output)


def test_alifestd_find_root_ids_does_not_mutate_input_dataframe():
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "ancestor_list": ["[none]", "[1]", "[2]"],
        }
    )
    input_df = phylogeny_df.copy()
    alifestd_find_root_ids(input_df)
    assert phylogeny_df.equals(input_df)


def test_alifestd_find_root_ids_returns_expected_output_with_single_root2():
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "ancestor_list": [[None], [1], [2]],
        }
    )
    expected_output = np.array([1])
    output = alifestd_find_root_ids(phylogeny_df)
    assert np.array_equal(output, expected_output)


def test_alifestd_find_root_ids_returns_expected_output_with_multiple_roots2():
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4],
            "ancestor_list": [[None], [None], [1], [2]],
        }
    )
    expected_output = np.array([1, 2])
    output = alifestd_find_root_ids(phylogeny_df)
    assert np.array_equal(output, expected_output)


def test_alifestd_find_root_ids_does_not_mutate_input_dataframe2():
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "ancestor_list": [[None], [1], [2]],
        }
    )
    input_df = phylogeny_df.copy()
    alifestd_find_root_ids(input_df)
    assert phylogeny_df.equals(input_df)
