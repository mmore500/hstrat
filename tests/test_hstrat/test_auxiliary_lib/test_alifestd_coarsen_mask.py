import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_coarsen_mask,
    alifestd_is_chronologically_sorted,
    alifestd_make_empty,
    alifestd_validate,
)


def make_asexual_phylo_df() -> pd.DataFrame:
    """Creates an example dataframe with 7 rows."""
    return pd.DataFrame(
        {
            "id": [*range(7)],
            "ancestor_list": [
                "[none]",
                "[0]",
                "[0]",
                "[1]",
                "[1]",
                "[2]",
                "[2]",
            ],
            "ancestor_id": [0, 0, 0, 1, 1, 2, 2],
        }
    )


@pytest.fixture  # wrapper because user cannot call fixtures directly
def asexual_phylo_df() -> pd.DataFrame:
    return make_asexual_phylo_df()


@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize("drop_ancestor_id", [True, False])
@pytest.mark.parametrize(
    "mask, expected_df",
    [
        # Everything is included in the mask
        (
            pd.Series([True] * 7),
            make_asexual_phylo_df(),
        ),
        # Root singleton dataframe
        (
            pd.Series([True, False, False, False, False, False, False]),
            pd.DataFrame(
                {"id": [0], "ancestor_list": ["[none]"], "ancestor_id": [0]}
            ),
        ),
        # Non-root singleton dataframe
        (
            pd.Series([False, True, False, False, False, False, False]),
            pd.DataFrame(
                {"id": [1], "ancestor_list": ["[none]"], "ancestor_id": [1]}
            ),
        ),
        # Nothing is included in the mask
        (
            pd.Series([False] * 7),
            alifestd_make_empty(ancestor_id=True),
        ),
        # Root is included in the mask
        (
            pd.Series([True, False, False, False, False, False, False]),
            pd.DataFrame(
                {"id": [0], "ancestor_list": ["[none]"], "ancestor_id": [0]}
            ),
        ),
        # Root is not included in the mask
        (
            pd.Series([False, True, True, True, True, True, True]),
            pd.DataFrame(
                {
                    "id": list(range(1, 7)),
                    "ancestor_list": [
                        "[none]",
                        "[none]",
                        "[1]",
                        "[1]",
                        "[2]",
                        "[2]",
                    ],
                    "ancestor_id": [1, 2, 1, 1, 2, 2],
                },
            ),
        ),
        # No leaves are included in the mask
        (
            pd.Series([True, True, True, True, True, False, False]),
            pd.DataFrame(
                {
                    "id": [*range(5)],
                    "ancestor_list": ["[none]", "[0]", "[0]", "[1]", "[1]"],
                    "ancestor_id": [0, 0, 0, 1, 1],
                }
            ),
        ),
        # All leaves are included in the mask
        (
            pd.Series([False, False, False, False, False, True, True]),
            pd.DataFrame(
                {
                    "id": [5, 6],
                    "ancestor_list": ["[none]", "[none]"],
                    "ancestor_id": [5, 6],
                },
            ),
        ),
        # One internal node excluded from mask
        (
            pd.Series([True, True, False, True, True, True, True]),
            pd.DataFrame(
                {
                    "id": [0, 1, 3, 4, 5, 6],
                    "ancestor_list": [
                        "[none]",
                        "[0]",
                        "[1]",
                        "[1]",
                        "[0]",
                        "[0]",
                    ],
                    "ancestor_id": [0, 0, 1, 1, 0, 0],
                },
            ),
        ),
        # All internal nodes excluded from mask
        (
            pd.Series([True, False, False, True, True, True, False]),
            pd.DataFrame(
                {
                    "id": [0, 3, 4, 5],
                    "ancestor_list": ["[none]", "[0]", "[0]", "[0]"],
                    "ancestor_id": [0, 0, 0, 0],
                },
            ),
        ),
    ],
)
def test_asexual_phylo_df(
    asexual_phylo_df: pd.DataFrame,
    mask: pd.Series,
    expected_df: pd.DataFrame,
    drop_ancestor_id: bool,
    mutate: bool,
):
    if drop_ancestor_id:
        asexual_phylo_df = asexual_phylo_df.drop("ancestor_id", axis=1)
        expected_df = expected_df.drop("ancestor_id", axis=1)

    original_df = asexual_phylo_df.copy()
    result_df = alifestd_coarsen_mask(asexual_phylo_df, mask, mutate=mutate)

    assert alifestd_validate(asexual_phylo_df)

    assert alifestd_validate(expected_df)
    pd.testing.assert_frame_equal(
        result_df, expected_df, check_index_type=False, check_like=True
    )
    if not mutate:
        pd.testing.assert_frame_equal(
            asexual_phylo_df,
            original_df,
            check_index_type=False,
            check_like=True,
        )


def make_sexual_phylo_df() -> pd.DataFrame:
    """Creates an example dataframe with 7 rows representing a sexual phylogeny."""
    return pd.DataFrame(
        {
            "id": [*range(7)],
            "ancestor_list": [
                "[none]",
                "[0]",
                "[0]",
                "[1, 2]",
                "[1, 2]",
                "[3]",
                "[3]",
            ],
        }
    )


@pytest.fixture  # wrapper because users cannot call fixtures directly
def sexual_phylo_df() -> pd.DataFrame:
    return make_sexual_phylo_df()


@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize(
    "mask, expected_df",
    [
        # Everything is included in the mask
        (
            pd.Series([True] * 7),
            make_sexual_phylo_df(),
        ),
        # Root singleton dataframe
        (
            pd.Series([True, False, False, False, False, False, False]),
            pd.DataFrame({"id": [0], "ancestor_list": ["[none]"]}),
        ),
        # Non-root singleton dataframe
        (
            pd.Series([False, True, False, False, False, False, False]),
            pd.DataFrame({"id": [1], "ancestor_list": ["[none]"]}),
        ),
        # A node with multiple ancestors
        (
            pd.Series([False, False, False, True, False, False, False]),
            pd.DataFrame({"id": [3], "ancestor_list": ["[none]"]}),
        ),
        # Exclude root, result has one ancestor for each entry except the first
        (
            pd.Series([False, True, True, True, True, True, True]),
            pd.DataFrame(
                {
                    "id": list(range(1, 7)),
                    "ancestor_list": [
                        "[none]",
                        "[none]",
                        "[1, 2]",
                        "[1, 2]",
                        "[3]",
                        "[3]",
                    ],
                },
            ),
        ),
        # Excluding one internal node and its descendants
        (
            pd.Series([True, True, True, False, False, False, False]),
            pd.DataFrame(
                {
                    "id": [*range(3)],
                    "ancestor_list": ["[none]", "[0]", "[0]"],
                }
            ),
        ),
        # Including only the leaves
        (
            pd.Series([False, False, False, False, False, True, True]),
            pd.DataFrame(
                {
                    "id": [5, 6],
                    "ancestor_list": ["[none]", "[none]"],
                },
            ),
        ),
        # Excluding internal nodes
        (
            pd.Series([True, False, False, False, False, True, True]),
            pd.DataFrame(
                {
                    "id": [0, 5, 6],
                    "ancestor_list": ["[none]", "[0]", "[0]"],
                },
            ),
        ),
        # One internal node excluded (with its descendants) from mask
        (
            pd.Series([True, True, False, True, True, False, False]),
            pd.DataFrame(
                {
                    "id": [0, 1, 3, 4],
                    "ancestor_list": [
                        "[none]",
                        "[0]",
                        "[0, 1]",
                        "[0, 1]",
                    ],
                },
            ),
        ),
    ],
)
def test_sexual_phylo_df(
    sexual_phylo_df: pd.DataFrame,
    mask: pd.Series,
    expected_df: pd.DataFrame,
    mutate: bool,
):
    original_df = sexual_phylo_df.copy()
    result_df = alifestd_coarsen_mask(sexual_phylo_df, mask, mutate=mutate)

    assert alifestd_validate(sexual_phylo_df)
    assert alifestd_validate(expected_df)
    pd.testing.assert_frame_equal(
        result_df, expected_df, check_index_type=False, check_like=True
    )
    if not mutate:
        pd.testing.assert_frame_equal(
            sexual_phylo_df,
            original_df,
            check_index_type=False,
            check_like=True,
        )
