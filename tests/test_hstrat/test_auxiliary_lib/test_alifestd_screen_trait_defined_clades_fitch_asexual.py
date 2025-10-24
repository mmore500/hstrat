import os
import typing

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_make_empty,
    alifestd_screen_trait_defined_clades_fitch_asexual,
    alifestd_to_working_format,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


def test_empty():
    phylogeny_df = alifestd_make_empty()
    phylogeny_df["origin_time"] = None
    res = alifestd_screen_trait_defined_clades_fitch_asexual(
        phylogeny_df,
        mask_trait_absent=[],
        mask_trait_present=[],
    )
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
        alifestd_screen_trait_defined_clades_fitch_asexual(
            phylogeny_df,
            mutate=mutate,
            mask_trait_absent=[True, False, False],
            mask_trait_present=[False, False, True],
        )

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple2(mutate: bool):
    # Tree structure:
    #        |---- 4 -
    #   |--- 0 --- 3 +
    #   1
    #   |--- 2 +
    phylogeny_df = pd.DataFrame(
        {
            "id": [3, 0, 1, 2, 4],
            "ancestor_list": ["[0]", "[1]", "[None]", "[1]", "[0]"],
            "origin_time": [50, 20, 10, 30, 40],
        },
    )
    original_df = phylogeny_df.copy()
    result = alifestd_screen_trait_defined_clades_fitch_asexual(
        phylogeny_df,
        mutate=mutate,
        mask_trait_present=[False, False, False, True, False],
        mask_trait_absent=[True, False, False, False, True],
    )
    assert not result[0]
    assert not result[1]
    assert not result[2]
    assert not result[3]
    assert not result[4]

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple3(apply: typing.Callable, mutate: bool):
    # Tree structure:
    #         0
    #       /   \
    #      1+    2
    #     / \   / \
    #    3   4 5   6
    #    -   + +   +
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
            "origin_time": [0, 10, 20, 40, 30, 50, 60],
        },
    )
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    result = alifestd_screen_trait_defined_clades_fitch_asexual(
        phylogeny_df,
        mutate=mutate,
        mask_trait_absent=[False, False, False, True, True, False, False],
        mask_trait_present=[False, True, False, False, False, True, True],
    )
    assert not result[0]
    assert not result[1]
    assert not result[2]
    assert not result[3]
    assert not result[4]
    assert not result[5]
    assert not result[6]

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple4(apply: typing.Callable, mutate: bool):
    # Tree structure:
    #         0-            7+
    #       /   \          / \
    #      1     2+       8+  9-
    #     / \
    #    3+  4
    #       / \
    #      5+  6+
    #
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            "ancestor_list": [
                "[None]",
                "[0]",
                "[0]",
                "[1]",
                "[1]",
                "[4]",
                "[4]",
                "[None]",
                "[7]",
                "[7]",
            ],
        },
    )
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    result = alifestd_screen_trait_defined_clades_fitch_asexual(
        phylogeny_df,
        mutate=mutate,
        mask_trait_present=[
            False,
            False,
            True,
            True,
            False,
            True,
            True,
            True,
            True,
            False,
        ],
        mask_trait_absent=[
            True,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            True,
        ],
    )
    assert not result[0]
    assert result[1]
    assert result[2]
    assert not result[3]
    assert not result[4]
    assert not result[5]
    assert not result[6]
    assert not result[7]
    assert not result[8]
    assert not result[9]

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple5(apply: typing.Callable, mutate: bool):
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
            "origin_time": [0, 10, 20, 40, 30, 50, 60],
        },
    )
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    result = alifestd_screen_trait_defined_clades_fitch_asexual(
        phylogeny_df,
        mutate=mutate,
        mask_trait_absent=[False, False, False, True, True, False, False],
        mask_trait_present=[False, True, False, False, False, True, True],
    )
    assert not result[0]
    assert not result[1]
    assert not result[2]
    assert not result[3]
    assert not result[4]
    assert not result[5]
    assert not result[6]

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple6(apply: typing.Callable, mutate: bool):
    # Tree structure:
    #         0
    #       /   \
    #      1+    2
    #     / \   / \
    #    3   4 5   6
    #    -   - +   -
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
            "origin_time": [0, 10, 20, 40, 30, 50, 60],
        },
    )
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    result = alifestd_screen_trait_defined_clades_fitch_asexual(
        phylogeny_df,
        mutate=mutate,
        mask_trait_absent=[False, False, False, True, True, False, True],
        mask_trait_present=[False, True, False, False, False, True, False],
    )
    assert not result[0]
    assert not result[1]
    assert not result[2]
    assert not result[3]
    assert not result[4]
    assert not result[5]
    assert not result[6]

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple7(apply: typing.Callable, mutate: bool):
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
            "origin_time": [0, 10, 20, 40, 30, 50, 60],
        },
    )
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    result = alifestd_screen_trait_defined_clades_fitch_asexual(
        phylogeny_df,
        mutate=mutate,
        mask_trait_absent=[False, False, False, True, True, False, True],
        mask_trait_present=[False, True, False, False, False, True, False],
    )
    assert not result[0]
    assert not result[1]
    assert not result[2]
    assert not result[3]
    assert not result[4]
    assert not result[5]
    assert not result[6]

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple8(apply: typing.Callable, mutate: bool):
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
            "origin_time": [0, 10, 20, 40, 30, 50, 60],
        },
    )
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    result = alifestd_screen_trait_defined_clades_fitch_asexual(
        phylogeny_df,
        mutate=mutate,
        mask_trait_absent=[False, False, False, False, False, False, False],
        mask_trait_present=[False, False, False, False, False, False, False],
    )
    assert not result[0]
    assert not result[1]
    assert not result[2]
    assert not result[3]
    assert not result[4]
    assert not result[5]
    assert not result[6]

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple9(apply: typing.Callable, mutate: bool):
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
            "origin_time": [0, 10, 20, 40, 30, 50, 60],
        },
    )
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    result = alifestd_screen_trait_defined_clades_fitch_asexual(
        phylogeny_df,
        mutate=mutate,
        mask_trait_absent=[False, False, False, False, False, False, False],
        mask_trait_present=[False, True, False, False, False, False, False],
    )
    assert not result[0]
    assert not result[1]
    assert not result[2]
    assert not result[3]
    assert not result[4]
    assert not result[5]
    assert not result[6]

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple10(mutate: bool):
    # Tree structure:
    #        |---- 4 +
    #   |--- 0 --- 3 +
    #   1
    #   |--- 2 -
    phylogeny_df = pd.DataFrame(
        {
            "id": [3, 0, 1, 2, 4],
            "ancestor_list": ["[0]", "[1]", "[None]", "[1]", "[0]"],
            "origin_time": [50, 20, 10, 30, 40],
        },
    )
    original_df = phylogeny_df.copy()
    result = alifestd_screen_trait_defined_clades_fitch_asexual(
        phylogeny_df,
        mutate=mutate,
        mask_trait_absent=[False, False, False, True, False],
        mask_trait_present=[True, False, False, False, True],
    )
    ids = phylogeny_df["id"].to_list()
    assert result[ids.index(0)]
    assert not result[ids.index(1)]
    assert not result[ids.index(2)]
    assert not result[ids.index(3)]
    assert not result[ids.index(4)]

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple11(mutate: bool):
    # Tree structure:
    #        |---- 4 +
    #   |--- 2 --- 3 +
    #   0
    #   |--- 1 -
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_id": [0, 0, 0, 2, 2],
            "origin_time": [0, 50, 20, 40, 40],
        },
    )
    original_df = phylogeny_df.copy()
    result = alifestd_screen_trait_defined_clades_fitch_asexual(
        phylogeny_df,
        mutate=mutate,
        mask_trait_absent=[False, True, False, False, False],
        mask_trait_present=[False, False, False, True, True],
    )
    ids = phylogeny_df["id"].to_list()
    assert not result[ids.index(0)]
    assert not result[ids.index(1)]
    assert result[ids.index(2)]
    assert not result[ids.index(3)]
    assert not result[ids.index(4)]

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple12(mutate: bool):
    # Tree structure:
    #        |---- 4 +
    #   |--- 2 --- 3 +
    #   0
    #   |--- 1 -
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_id": [0, 0, 0, 2, 2],
            "origin_time": [0, 50, 20, 40, 40],
        },
    )
    original_df = phylogeny_df.copy()
    result = alifestd_screen_trait_defined_clades_fitch_asexual(
        phylogeny_df,
        mutate=mutate,
        mask_trait_absent=[False, True, False, False, False],
        mask_trait_present=[False, False, True, True, True],
    )
    ids = phylogeny_df["id"].to_list()
    assert not result[ids.index(0)]
    assert not result[ids.index(1)]
    assert result[ids.index(2)]
    assert not result[ids.index(3)]
    assert not result[ids.index(4)]

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple13(mutate: bool):
    # Tree structure:
    #        |---- 4 +
    #   |--- 2 --- 3 +
    #   0
    #   |--- 1
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_id": [0, 0, 0, 2, 2],
            "origin_time": [0, 50, 20, 40, 40],
        },
    )
    original_df = phylogeny_df.copy()
    result = alifestd_screen_trait_defined_clades_fitch_asexual(
        phylogeny_df,
        mutate=mutate,
        mask_trait_absent=[False, False, False, False, False],
        mask_trait_present=[False, False, True, True, True],
    )
    ids = phylogeny_df["id"].to_list()
    assert not result[ids.index(0)]
    assert not result[ids.index(1)]
    assert not result[ids.index(2)]
    assert not result[ids.index(3)]
    assert not result[ids.index(4)]

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple14(apply: typing.Callable, mutate: bool):
    # Tree structure:
    #         0
    #       /   \
    #      1-    2
    #     / \   / \
    #    3   4 5   6
    #    -   + +   +
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
            "origin_time": [0, 10, 20, 40, 30, 50, 60],
        },
    )
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    result = alifestd_screen_trait_defined_clades_fitch_asexual(
        phylogeny_df,
        mutate=mutate,
        mask_trait_absent=[False, True, False, True, False, False, False],
        mask_trait_present=[False, False, False, False, True, True, True],
    )
    assert not result[0]
    assert not result[1]
    assert result[2]
    assert not result[3]
    assert result[4]
    assert not result[5]
    assert not result[6]

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple15(apply: typing.Callable, mutate: bool):
    # Tree structure:
    #         0-
    #       /   \
    #      1+    2
    #     / \   / \
    #    3   4 5   6
    #    -   - +   +
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
            "origin_time": [0, 10, 20, 40, 30, 50, 60],
        },
    )
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    result = alifestd_screen_trait_defined_clades_fitch_asexual(
        phylogeny_df,
        mutate=mutate,
        mask_trait_absent=[True, False, False, True, True, False, False],
        mask_trait_present=[False, True, False, False, False, True, True],
    )
    assert not result[0]
    assert result[1]
    assert result[2]
    assert not result[3]
    assert not result[4]
    assert not result[5]
    assert not result[6]

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple16(apply: typing.Callable, mutate: bool):
    # Tree structure:
    #         0
    #       /   \
    #      1+    2-
    #     / \   / \
    #    3   4 5   6
    #    -   - +   -
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
            "origin_time": [0, 10, 20, 40, 30, 50, 60],
        },
    )
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    result = alifestd_screen_trait_defined_clades_fitch_asexual(
        phylogeny_df,
        mutate=mutate,
        mask_trait_absent=[False, False, True, True, True, False, True],
        mask_trait_present=[False, True, False, False, False, True, False],
    )
    assert not result[0]
    assert result[1]
    assert not result[2]
    assert not result[3]
    assert not result[4]
    assert result[5]
    assert not result[6]

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple17(apply: typing.Callable, mutate: bool):
    # Tree structure:
    #         0+            7-
    #       /   \          / \
    #      1     2-       8-  9+
    #     / \
    #    3-  4
    #       / \
    #      5-  6-
    #
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            "ancestor_list": [
                "[None]",
                "[0]",
                "[0]",
                "[1]",
                "[1]",
                "[4]",
                "[4]",
                "[None]",
                "[7]",
                "[7]",
            ],
        },
    )
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    result = alifestd_screen_trait_defined_clades_fitch_asexual(
        phylogeny_df,
        mutate=mutate,
        mask_trait_present=[
            True,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            True,
        ],
        mask_trait_absent=[
            False,
            False,
            False,
            True,
            False,
            True,
            True,
            True,
            True,
            False,
        ],
    )
    assert not result[0]
    assert not result[1]
    assert not result[2]
    assert not result[3]
    assert not result[4]
    assert not result[5]
    assert not result[6]
    assert not result[7]
    assert not result[8]
    assert result[9]

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple18(apply: typing.Callable, mutate: bool):
    # Tree structure:
    #         0             7
    #       /   \          / \
    #      1     2-       8-  9+
    #     / \
    #    3-  4
    #       / \
    #      5-  6-
    #
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            "ancestor_list": [
                "[None]",
                "[0]",
                "[0]",
                "[1]",
                "[1]",
                "[4]",
                "[4]",
                "[None]",
                "[7]",
                "[7]",
            ],
        },
    )
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    result = alifestd_screen_trait_defined_clades_fitch_asexual(
        phylogeny_df,
        mutate=mutate,
        mask_trait_present=[
            True,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            True,
        ],
        mask_trait_absent=[
            False,
            False,
            False,
            True,
            False,
            True,
            True,
            True,
            True,
            False,
        ],
    )
    assert not result[0]
    assert not result[1]
    assert not result[2]
    assert not result[3]
    assert not result[4]
    assert not result[5]
    assert not result[6]
    assert not result[7]
    assert not result[8]
    assert result[9]

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple19(apply: typing.Callable, mutate: bool):
    # Tree structure:
    #         0-
    #       /   \
    #      1-    2-
    #     / \   / \
    #    3   4 5   6
    #
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_id": [0, 0, 0, 1, 1, 2, 2],
        },
    )
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    result = alifestd_screen_trait_defined_clades_fitch_asexual(
        phylogeny_df,
        mutate=mutate,
        mask_trait_absent=[True, True, True, False, False, False, False],
        mask_trait_present=[False, False, False, False, False, False, False],
    )
    assert not result[0]
    assert not result[1]
    assert not result[2]
    assert not result[3]
    assert not result[4]
    assert not result[5]
    assert not result[6]

    if not mutate:
        assert original_df.equals(phylogeny_df)
