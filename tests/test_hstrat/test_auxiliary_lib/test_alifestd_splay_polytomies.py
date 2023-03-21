import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_assign_contiguous_ids,
    alifestd_make_empty,
    alifestd_splay_polytomies,
    alifestd_try_add_ancestor_id_col,
    alifestd_validate,
)


def test_alifestd_splay_polytomies_empty():
    pd.testing.assert_frame_equal(
        alifestd_splay_polytomies(alifestd_make_empty()).reset_index(
            drop=True
        ),
        alifestd_try_add_ancestor_id_col(alifestd_make_empty()).reset_index(
            drop=True
        ),
    )


def test_alifestd_splay_polytomies_singleton():
    df = pd.DataFrame(
        {
            "id": [0],
            "ancestor_list": ["[none]"],
            "ancestor_id": [0],
            "trait": [1.2],
        }
    )
    expected_df = df.copy()
    result_df = alifestd_splay_polytomies(df, mutate=False)
    alifestd_validate(result_df)
    pd.testing.assert_frame_equal(result_df, expected_df)


@pytest.mark.parametrize("shuffle", [True, False])
def test_alifestd_splay_polytomies_no_polytomies(shuffle):
    # Test case for a phylogeny dataframe with only bifurcations
    #    99
    #  /   \
    # 2     3
    #     /   \
    #    4     5
    df = pd.DataFrame(
        {
            "id": [99, 2, 3, 4, 5],
            "ancestor_list": ["[none]", "[99]", "[99]", "[3]", "[3]"],
            "ancestor_id": [99, 99, 99, 3, 3],
            "trait": [1.2, 3.1, 2.5, 1.7, 0.9],
        }
    )
    if shuffle:
        df = df.sample(frac=1).reset_index(drop=True)
    expected_df = df.copy()
    result_df = alifestd_splay_polytomies(df, mutate=False)
    alifestd_validate(result_df)
    pd.testing.assert_frame_equal(result_df, expected_df)


@pytest.mark.parametrize("shuffle", [True, False])
def test_alifestd_splay_polytomies_no_polytomies_unifurcation(shuffle):
    # Test case for a phylogeny dataframe with no polytomies,
    # but with unifurcations
    #    0
    #    |
    #    1
    #  /   \
    # 2     4
    # |     |
    # 5     7
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 4, 5, 7],
            "ancestor_list": [
                "[none]",
                "[0]",
                "[1]",
                "[1]",
                "[2]",
                "[4]",
            ],
            "ancestor_id": [0, 0, 1, 1, 2, 4],
            "trait": [1.2, 3.1, 2.5, 0.9, 12.1, 9.9],
        }
    )
    if shuffle:
        df = df.sample(frac=1).reset_index(drop=True)
    expected_df = df.copy()
    result_df = alifestd_splay_polytomies(df, mutate=False)
    alifestd_validate(result_df)
    pd.testing.assert_frame_equal(result_df, expected_df)


@pytest.mark.parametrize("shuffle", [True, False])
def test_alifestd_splay_polytomies_no_polytomies_only_unifurcation(shuffle):
    # Test case for a phylogeny dataframe with only unifurcations
    #    0
    #    |
    #    1
    #    |
    #    2
    #    |
    #    3
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_list": [
                "[none]",
                "[0]",
                "[1]",
                "[2]",
            ],
            "ancestor_id": [0, 0, 1, 2],
            "trait": [1.2, 3.1, 2.5, 0.9],
        }
    )
    if shuffle:
        df = df.sample(frac=1).reset_index(drop=True)
    expected_df = df.copy()
    result_df = alifestd_splay_polytomies(df, mutate=False)
    alifestd_validate(result_df)
    pd.testing.assert_frame_equal(result_df, expected_df)


@pytest.mark.parametrize("rotate", [True, False])
def test_alifestd_splay_polytomies_one_polytomy_of_size_three(rotate):
    # Test case for a phylogeny dataframe with one polytomy of size three
    #   1
    #  /|\
    # 2 3 4
    df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4],
            "ancestor_list": ["[none]", "[1]", "[1]", "[1]"],
            "ancestor_id": [1, 1, 1, 1],
            "trait": [1.2, 3.1, 2.5, 1.7],
            "origin_time": [0, 1, 1, 1],
        }
    )
    if rotate:
        df = pd.concat([df.iloc[1:], df.iloc[:1]]).reset_index(drop=True)
        assert len(df) == 4
    #   1
    #  / \
    # 2   5
    #    /  \
    #   3    4
    expected_df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "ancestor_list": ["[none]", "[1]", "[5]", "[5]", "[1]"],
            "ancestor_id": [1, 1, 5, 5, 1],
            "trait": [1.2, 3.1, 2.5, 1.7, 1.2],
            "origin_time": [0, 1, 1, 1, 0],
        }
    )
    result_df = alifestd_splay_polytomies(df, mutate=False)
    alifestd_validate(result_df)
    pd.testing.assert_frame_equal(
        result_df.sort_values("id").reset_index(drop=True),
        expected_df.sort_values("id").reset_index(drop=True),
    )


def test_alifestd_splay_polytomies_one_polytomy_of_size_three_with_unifurcation():
    # Test case for a phylogeny dataframe with one polytomy of size three
    # and unifurcations
    #    1
    #  / | \
    # 2  0  3
    # |     |
    # 4     5
    #       |
    #       6
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_list": [
                "[1]",
                "[none]",
                "[1]",
                "[1]",
                "[2]",
                "[3]",
                "[5]",
            ],
            "ancestor_id": [1, 1, 1, 1, 2, 3, 5],
            "trait": [1.2, 3.1, 2.5, 1.7, 0.9, 101.9, 22.0],
        }
    )
    #    1
    #  /   \
    # 0     7
    #     /   \
    #    2     3
    #    |     |
    #    4     5
    #          |
    #          6
    expected_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6, 7],
            "ancestor_list": [
                "[1]",
                "[none]",
                "[7]",
                "[7]",
                "[2]",
                "[3]",
                "[5]",
                "[1]",
            ],
            "ancestor_id": [1, 1, 7, 7, 2, 3, 5, 1],
            "trait": [1.2, 3.1, 2.5, 1.7, 0.9, 101.9, 22.0, 3.1],
        }
    )
    result_df = alifestd_splay_polytomies(df, mutate=False)
    alifestd_validate(result_df)
    pd.testing.assert_frame_equal(result_df, expected_df)

    result_df = alifestd_splay_polytomies(
        df.reindex([0, 1, 2, 4, 3, 5, 6]), mutate=False
    )
    alifestd_validate(result_df)
    pd.testing.assert_frame_equal(
        result_df,
        expected_df.reindex([0, 1, 2, 4, 3, 5, 6, 7]).reset_index(drop=True),
    )


def test_alifestd_splay_polytomies_two_polytomies_with_unifurcation():
    # Test case for a phylogeny dataframe with two polytomies, one of size
    # three and one of size four, and a unifurcation
    #    0
    #    | \
    #    1  10
    #  / | \
    # 2  3  4
    # |    /||\
    # 5   / || \
    #    / / | |
    #   6 7  8 9
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "ancestor_list": [
                "[none]",
                "[0]",
                "[1]",
                "[1]",
                "[1]",
                "[2]",
                "[4]",
                "[4]",
                "[4]",
                "[4]",
                "[0]",
            ],
            "ancestor_id": [0, 0, 1, 1, 1, 2, 4, 4, 4, 4, 0],
        }
    )
    #    0
    #    | \
    #    1  10
    #  /   \
    # 2     11
    # |    /  \
    # 5   3    4
    #         / \
    #        6   12
    #           /  \
    #          7    13
    #              /  \
    #             8    9
    expected_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
            "ancestor_list": [
                "[none]",
                "[0]",
                "[1]",
                "[11]",
                "[11]",
                "[2]",
                "[4]",
                "[12]",
                "[13]",
                "[13]",
                "[0]",
                "[1]",
                "[4]",
                "[12]",
            ],
            "ancestor_id": [0, 0, 1, 11, 11, 2, 4, 12, 13, 13, 0, 1, 4, 12],
        }
    )
    result_df = alifestd_assign_contiguous_ids(
        alifestd_splay_polytomies(df, mutate=False)
    )
    alifestd_validate(result_df)
    pd.testing.assert_frame_equal(result_df, expected_df)


@pytest.mark.parametrize(
    "df",
    [
        pd.DataFrame(
            {
                "id": [99, 2, 3, 4, 5],
                "ancestor_list": ["[none]", "[99]", "[99]", "[3]", "[3]"],
                "ancestor_id": [99, 99, 99, 3, 3],
                "trait": [1.2, 3.1, 2.5, 1.7, 0.9],
            }
        ),  #  <- no polytomies
        pd.DataFrame(
            {
                "id": [0, 1, 2, 3, 4, 5, 6],
                "ancestor_list": [
                    "[1]",
                    "[none]",
                    "[1]",
                    "[1]",
                    "[2]",
                    "[3]",
                    "[5]",
                ],
                "ancestor_id": [1, 1, 1, 1, 2, 3, 5],
                "trait": [1.2, 3.1, 2.5, 1.7, 0.9, 101.9, 22.0],
            }
        ),  #  <- has polytomy
    ],
)
def test_alifestd_splay_polytomies_mutate(df):
    df_ = df.copy()
    alifestd_splay_polytomies(df, mutate=False)
    pd.testing.assert_frame_equal(df_, df)
