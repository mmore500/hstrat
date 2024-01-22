import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_calc_polytomic_index,
    alifestd_make_empty,
)


def test_empty_df():
    assert alifestd_calc_polytomic_index(alifestd_make_empty()) == 0


def test_singleton_df():
    df = pd.DataFrame(
        {
            "id": [0],
            "ancestor_list": [[None]],
        }
    )
    assert alifestd_calc_polytomic_index(df) == 0


def test_polytomy_df1():
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_list": [[None], [0], [0], [0], [1]],
        }
    )
    assert alifestd_calc_polytomic_index(df) == 1


def test_polytomy_df2():
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_list": [[None], [0], [0], [0], [1], [1], [1]],
        }
    )
    assert alifestd_calc_polytomic_index(df) == 2


def test_polytomy_df3():
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6, 7],
            "ancestor_list": [[None], [0], [0], [0], [1], [1], [1], [1]],
        }
    )
    assert alifestd_calc_polytomic_index(df) == 3


def test_multiple_trees_df1():
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5],
            "ancestor_list": [[None], [None], [0], [2], [2], [3]],
        }
    )
    assert alifestd_calc_polytomic_index(df) == 0


def test_multiple_trees_df2():
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5],
            "ancestor_list": [[None], [None], [0], [1], [0], [0]],
        }
    )
    assert alifestd_calc_polytomic_index(df) == 1


def test_multiple_trees_df3():
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_list": [[None], [None], [0], [1], [0], [0], [None]],
        }
    )
    assert alifestd_calc_polytomic_index(df) == 1


def test_sexual():
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 5],
            "ancestor_list": [[None], [None], [0, 1], [1], [0]],
        }
    )
    with pytest.raises(ValueError):
        alifestd_calc_polytomic_index(df)
