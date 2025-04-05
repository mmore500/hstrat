import os
import typing

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_collapse_unifurcations,
    alifestd_delete_unifurcating_roots_asexual,
    alifestd_make_empty,
    alifestd_splay_polytomies,
    alifestd_to_working_format,
    alifestd_unfurl_traversal_inorder_asexual,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        pd.read_csv(
            f"{assets_path}/example-standard-toy-asexual-phylogeny.csv"
        ),
        pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv"),
        pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv"),
        pd.read_csv(f"{assets_path}/nk_tournamentselection.csv"),
    ],
)
def test_fuzz(phylogeny_df: pd.DataFrame):
    phylogeny_df = alifestd_splay_polytomies(phylogeny_df)
    phylogeny_df = alifestd_collapse_unifurcations(phylogeny_df)
    phylogeny_df = alifestd_delete_unifurcating_roots_asexual(phylogeny_df)
    original = phylogeny_df.copy()

    result = alifestd_unfurl_traversal_inorder_asexual(phylogeny_df)

    # Confirm that the input dataframe is not mutated.
    assert original.equals(phylogeny_df)

    # Verify that result is a permutation of the phylogeny IDs.
    assert len(result) == len(phylogeny_df)
    assert set(result) == set(phylogeny_df["id"])


def test_empty():
    res = alifestd_unfurl_traversal_inorder_asexual(alifestd_make_empty())
    assert len(res) == 0


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple1(apply: typing.Callable, mutate: bool):
    # Chain tree: 0 -> 1 -> 2
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[1]"],
        },
    )
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    with pytest.raises(ValueError):
        alifestd_unfurl_traversal_inorder_asexual(
            phylogeny_df,
            mutate=mutate,
        )

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple2(mutate: bool):
    # Tree structure:
    #        |---- 4
    #   |--- 0 --- 3
    #   1
    #   |--- 2
    phylogeny_df = pd.DataFrame(
        {
            "id": [3, 0, 1, 2, 4],
            "ancestor_list": ["[0]", "[1]", "[None]", "[1]", "[0]"],
        },
    )
    original_df = phylogeny_df.copy()
    result = alifestd_unfurl_traversal_inorder_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    valid_orders = {
        (3, 0, 4, 1, 2),
        (4, 0, 3, 1, 2),
        (2, 1, 3, 0, 4),
        (2, 1, 4, 0, 3),
    }
    assert tuple(result) in valid_orders

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple4(apply: typing.Callable, mutate: bool):
    # Tree structure:
    #         0
    #       /   \
    #      1     2
    #     / \   / \
    #    3   4 5   6
    #

    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_list": [
                "[None]",
                "[0]",
                "[0]",
                "[1]",
                "[1]",
                "[2]",
                "[2]",
            ],
        },
    )
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    result = alifestd_unfurl_traversal_inorder_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    valid_orders = {
        (3, 1, 4, 0, 5, 2, 6),
        (4, 1, 3, 0, 5, 2, 6),
        (3, 1, 4, 0, 6, 2, 5),
        (4, 1, 3, 0, 5, 2, 5),
        (5, 2, 6, 0, 3, 1, 4),
        (5, 2, 6, 0, 4, 1, 3),
        (6, 2, 5, 0, 3, 1, 4),
        (5, 2, 5, 0, 4, 1, 3),
    }
    assert tuple(result.tolist()) in valid_orders

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple5(apply: typing.Callable, mutate: bool):
    # Tree structure:
    #         0
    #       /   \
    #      1     2
    #     / \
    #    3   4
    #       / \
    #      5   6

    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_list": [
                "[None]",
                "[0]",
                "[0]",
                "[1]",
                "[1]",
                "[4]",
                "[4]",
            ],
        },
    )
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    result = alifestd_unfurl_traversal_inorder_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    valid_orders = {
        (5, 4, 6, 1, 3, 0, 2),
        (6, 4, 5, 1, 3, 0, 2),
        (3, 1, 5, 4, 6, 0, 2),
        (3, 1, 6, 4, 5, 0, 2),
        (2, 0, 5, 4, 6, 1, 3),
        (2, 0, 6, 4, 5, 1, 3),
        (2, 0, 3, 1, 5, 4, 6),
        (2, 0, 3, 1, 6, 4, 5),
    }
    assert tuple(result.tolist()) in valid_orders

    if not mutate:
        assert original_df.equals(phylogeny_df)
