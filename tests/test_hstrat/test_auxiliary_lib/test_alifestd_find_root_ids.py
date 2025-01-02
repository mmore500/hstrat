import typing

import numpy as np
import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_find_root_ids,
    alifestd_make_empty,
    alifestd_try_add_ancestor_id_col,
)


@pytest.mark.parametrize(
    "apply", [alifestd_try_add_ancestor_id_col, lambda x: x]
)
def test_no_root(apply: typing.Callable):
    assert np.array_equal(
        alifestd_find_root_ids(apply(alifestd_make_empty())),
        np.array([]),
    )


@pytest.mark.parametrize(
    "apply", [alifestd_try_add_ancestor_id_col, lambda x: x]
)
def test_singleton(apply: typing.Callable):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0],
            "ancestor_list": ["[none]"],
        }
    )
    phylogeny_df = apply(phylogeny_df)
    assert np.array_equal(alifestd_find_root_ids(phylogeny_df), np.array([0]))


@pytest.mark.parametrize(
    "apply", [alifestd_try_add_ancestor_id_col, lambda x: x]
)
def test_alifestd_find_root_ids_returns_expected_output_with_single_root1(
    apply: typing.Callable,
):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "ancestor_list": ["[none]", "[1]", "[2]"],
        }
    )
    phylogeny_df = apply(phylogeny_df)

    expected_output = np.array([1])
    output = alifestd_find_root_ids(phylogeny_df)
    assert np.array_equal(output, expected_output)


@pytest.mark.parametrize(
    "apply", [alifestd_try_add_ancestor_id_col, lambda x: x]
)
def test_alifestd_find_root_ids_returns_expected_output_with_multiple_roots1(
    apply: typing.Callable,
):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4],
            "ancestor_list": ["[none]", "[none]", "[1]", "[2]"],
        }
    )
    phylogeny_df = apply(phylogeny_df)
    expected_output = np.array([1, 2])
    output = alifestd_find_root_ids(phylogeny_df)
    assert np.array_equal(output, expected_output)


def test_alifestd_find_root_ids_returns_expected_output_with_single_root2():
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "ancestor_list": ["[none]", "[1]", "[2, 1]"],
        }
    )
    expected_output = np.array([1])
    output = alifestd_find_root_ids(phylogeny_df)
    assert np.array_equal(output, expected_output)


def test_alifestd_find_root_ids_returns_expected_output_with_multiple_roots2():
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4],
            "ancestor_list": ["[none]", "[none]", "[1]", "[2, 1]"],
        }
    )
    expected_output = np.array([1, 2])
    output = alifestd_find_root_ids(phylogeny_df)
    assert np.array_equal(output, expected_output)


@pytest.mark.parametrize(
    "apply", [alifestd_try_add_ancestor_id_col, lambda x: x]
)
def test_alifestd_find_root_ids_does_not_mutate_input_dataframe(
    apply: typing.Callable,
):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "ancestor_list": ["[none]", "[1]", "[2]"],
        }
    )
    phylogeny_df = apply(phylogeny_df)
    input_df = phylogeny_df.copy()
    alifestd_find_root_ids(input_df)
    assert phylogeny_df.equals(input_df)


@pytest.mark.parametrize(
    "apply", [alifestd_try_add_ancestor_id_col, lambda x: x]
)
def test_alifestd_find_root_ids_returns_expected_output_with_single_root3(
    apply: typing.Callable,
):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "ancestor_list": [[None], [1], [2]],
        }
    )
    phylogeny_df = apply(phylogeny_df)
    expected_output = np.array([1])
    output = alifestd_find_root_ids(phylogeny_df)
    assert np.array_equal(output, expected_output)


@pytest.mark.parametrize(
    "apply", [alifestd_try_add_ancestor_id_col, lambda x: x]
)
def test_alifestd_find_root_ids_returns_expected_output_with_multiple_roots3(
    apply: typing.Callable,
):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4],
            "ancestor_list": [[None], [None], [1], [2]],
        }
    )
    phylogeny_df = apply(phylogeny_df)
    expected_output = np.array([1, 2])
    output = alifestd_find_root_ids(phylogeny_df)
    assert np.array_equal(output, expected_output)


@pytest.mark.parametrize(
    "apply", [alifestd_try_add_ancestor_id_col, lambda x: x]
)
def test_alifestd_find_root_ids_does_not_mutate_input_dataframe3(
    apply: typing.Callable,
):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "ancestor_list": [[None], [1], [2]],
        }
    )
    phylogeny_df = apply(phylogeny_df)
    input_df = phylogeny_df.copy()
    alifestd_find_root_ids(input_df)
    assert phylogeny_df.equals(input_df)
