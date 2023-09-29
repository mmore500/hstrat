import pandas as pd

from hstrat._auxiliary_lib import (
    alifestd_has_increasing_ids,
    alifestd_make_empty,
)


def test_empty():
    assert alifestd_has_increasing_ids(alifestd_make_empty())


def test_singleton():
    df = pd.DataFrame({"id": [2], "ancestor_id": [2]})
    assert alifestd_has_increasing_ids(df)

    df = pd.DataFrame({"id": [0], "ancestor_list": ["[None]"]})
    assert alifestd_has_increasing_ids(df)


def test_ancestor_id_column_present():
    df = pd.DataFrame({"id": [2, 3, 4, 5], "ancestor_id": [2, 2, 3, 4]})
    assert alifestd_has_increasing_ids(df)

    df_false_case = pd.DataFrame(
        {"id": [2, 3, 4, 5], "ancestor_id": [2, 2, 5, 2]}
    )
    assert not alifestd_has_increasing_ids(df_false_case)


def test_ancestor_list_column_present():
    df = pd.DataFrame(
        {"id": [2, 3, 4, 5], "ancestor_list": ["[2]", "[2]", "[3,2]", "[4,3]"]}
    )
    assert alifestd_has_increasing_ids(df)

    df_false_case = pd.DataFrame(
        {"id": [2, 3, 4, 5], "ancestor_list": ["[2]", "[2,4]", "[2]", "[4,3]"]}
    )
    assert not alifestd_has_increasing_ids(df_false_case)
