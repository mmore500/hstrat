import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_collapse_trunk_asexual,
    alifestd_validate,
)


@pytest.mark.parametrize("mutate", [True, False])
def test_alifestd_collapse_trunk_asexual_no_trunk_column(mutate: bool):
    df = pd.DataFrame(
        {
            "id": [0],
            "ancestor_list": ["[none]"],
        }
    )
    with pytest.raises(ValueError):
        alifestd_collapse_trunk_asexual(df, mutate=mutate)


@pytest.mark.parametrize("mutate", [True, False])
def test_alifestd_collapse_trunk_asexual_single_trunk(mutate: bool):
    df = pd.DataFrame(
        {
            "id": [0],
            "ancestor_list": ["[]"],
            "is_trunk": [True],
        }
    )
    original_df = df.copy()
    result = alifestd_collapse_trunk_asexual(df, mutate=mutate)
    assert alifestd_validate(result)
    pd.testing.assert_frame_equal(result[df.columns], df)

    if not mutate:
        assert original_df.equals(df)


@pytest.mark.parametrize("mutate", [True, False])
def test_alifestd_collapse_trunk_asexual_no_collapse_needed1(mutate: bool):
    df = pd.DataFrame(
        {
            "id": [0, 8],
            "ancestor_id": [0, 0],
            "ancestor_list": ["[none]", "[0]"],
            "is_trunk": [True, False],
        }
    )
    original_df = df.copy()
    result = alifestd_collapse_trunk_asexual(df)
    assert alifestd_validate(result)
    pd.testing.assert_frame_equal(
        result[df.columns].reset_index(drop=True), df
    )

    if not mutate:
        assert original_df.equals(df)


@pytest.mark.parametrize("mutate", [True, False])
def test_alifestd_collapse_trunk_asexual_no_collapse_needed2(mutate: bool):
    df = pd.DataFrame(
        {
            "id": [0, 1],
            "ancestor_list": ["[none]", "[0]"],
            "is_trunk": [True, True],
        }
    )
    original_df = df.copy()
    result = alifestd_collapse_trunk_asexual(df)
    assert alifestd_validate(result)

    expected = pd.DataFrame(
        {
            "id": [0],
            "ancestor_list": ["[none]"],
            "is_trunk": [True],
        }
    )
    pd.testing.assert_frame_equal(result[expected.columns], expected)

    if not mutate:
        assert original_df.equals(df)


@pytest.mark.parametrize("mutate", [True, False])
def test_alifestd_collapse_trunk_asexual_no_collapse_needed3(mutate: bool):
    df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_id": [0, 0, 1],
            "ancestor_list": ["[none]", "[0]", "[1]"],
            "is_trunk": [False, False, False],
        }
    )
    original_df = df.copy()
    result = alifestd_collapse_trunk_asexual(df)
    assert alifestd_validate(result)
    pd.testing.assert_frame_equal(result[df.columns], df)

    if not mutate:
        assert df.equals(original_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_alifestd_collapse_trunk_asexual_collapse1(mutate: bool):
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 4, 3, 5],
            "ancestor_id": [0, 0, 1, 2, 0, 5],
            "ancestor_list": ["[none]", "[0]", "[1]", "[2]", "[0]", "[none]"],
            "is_trunk": [True, True, True, False, False, False],
        }
    )
    original_df = df.copy()
    result = alifestd_collapse_trunk_asexual(df)
    assert alifestd_validate(result)

    expected = pd.DataFrame(
        {
            "id": [0, 4, 3, 5],
            "ancestor_id": [0, 0, 0, 5],
            "ancestor_list": ["[none]", "[0]", "[0]", "[none]"],
            "is_trunk": [True, False, False, False],
        }
    )
    pd.testing.assert_frame_equal(result[expected.columns], expected)

    if not mutate:
        assert df.equals(original_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_alifestd_collapse_trunk_asexual_collapse2(mutate: bool):
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_list": [
                "[none]",
                "[0]",
                "[1]",
                "[0]",
                "[0]",
                "[2]",
                "[3]",
            ],
            "is_trunk": [True, True, True, False, True, True, False],
        }
    )
    original_df = df.copy()
    result = alifestd_collapse_trunk_asexual(df)
    assert alifestd_validate(result)

    expected = pd.DataFrame(
        {
            "id": [0, 3, 6],
            "ancestor_list": ["[none]", "[0]", "[3]"],
            "is_trunk": [True, False, False],
        }
    )
    pd.testing.assert_frame_equal(result[expected.columns], expected)

    if not mutate:
        assert df.equals(original_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_alifestd_collapse_trunk_asexual_noncontiguous_trunk(mutate: bool):
    df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[1]"],
            "is_trunk": [True, False, True],
        }
    )
    original_df = df.copy()
    with pytest.raises(ValueError):
        alifestd_collapse_trunk_asexual(df)

    if not mutate:
        assert df.equals(original_df)
