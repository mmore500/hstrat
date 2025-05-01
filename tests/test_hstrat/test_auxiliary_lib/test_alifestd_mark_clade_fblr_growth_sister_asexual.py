import math
import os
import typing

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_collapse_unifurcations,
    alifestd_delete_unifurcating_roots_asexual,
    alifestd_join_roots,
    alifestd_make_empty,
    alifestd_mark_clade_fblr_growth_sister_asexual,
    alifestd_splay_polytomies,
    alifestd_to_working_format,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


def test_empty():
    phylogeny_df = alifestd_make_empty()
    phylogeny_df["origin_time"] = None
    res = alifestd_mark_clade_fblr_growth_sister_asexual(
        phylogeny_df,
    )
    assert len(res) == 0


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize("parallel_backend", [None, "loky"])
def test_simple1(
    apply: typing.Callable,
    mutate: bool,
    parallel_backend: typing.Optional[str],
):
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
        alifestd_mark_clade_fblr_growth_sister_asexual(
            phylogeny_df,
            mutate=mutate,
            parallel_backend=parallel_backend,
        )

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize("parallel_backend", [None, "loky"])
def test_simple2(mutate: bool, parallel_backend: typing.Optional[str]):
    # Tree structure:
    #        |---- 4
    #   |--- 0 --- 3
    #   1
    #   |--- 2
    phylogeny_df = pd.DataFrame(
        {
            "id": [3, 0, 1, 2, 4],
            "ancestor_list": ["[0]", "[1]", "[None]", "[1]", "[0]"],
            "origin_time": [50, 20, 10, 30, 40],
        },
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_clade_fblr_growth_sister_asexual(
        phylogeny_df,
        mutate=mutate,
        parallel_backend=parallel_backend,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[3, "clade_fblr_growth_sister"] > 0
    assert result_df.loc[0, "clade_fblr_growth_sister"] > 0
    assert math.isnan(result_df.loc[1, "clade_fblr_growth_sister"])
    assert result_df.loc[2, "clade_fblr_growth_sister"] < 0
    assert result_df.loc[4, "clade_fblr_growth_sister"] < 0

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize("parallel_backend", [None, "loky"])
def test_simple4(
    apply: typing.Callable,
    mutate: bool,
    parallel_backend: typing.Optional[str],
):
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
    result_df = alifestd_mark_clade_fblr_growth_sister_asexual(
        phylogeny_df,
        mutate=mutate,
        parallel_backend=parallel_backend,
    )
    result_df.index = result_df["id"]
    assert math.isnan(result_df.loc[0, "clade_fblr_growth_sister"])
    assert result_df.loc[1, "clade_fblr_growth_sister"] < 0
    assert result_df.loc[2, "clade_fblr_growth_sister"] > 0
    assert result_df.loc[3, "clade_fblr_growth_sister"] > 0
    assert result_df.loc[4, "clade_fblr_growth_sister"] < 0
    assert result_df.loc[5, "clade_fblr_growth_sister"] < 0
    assert result_df.loc[6, "clade_fblr_growth_sister"] > 0

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize("parallel_backend", [None, "loky"])
def test_simple5(
    apply: typing.Callable,
    mutate: bool,
    parallel_backend: typing.Optional[str],
):
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
            "origin_time": [0, 10, 200, 30, 40, 50, 60],
        },
    )
    phylogeny_df = apply(phylogeny_df)
    phylogeny_df.copy()
    result_df = alifestd_mark_clade_fblr_growth_sister_asexual(
        phylogeny_df,
        mutate=mutate,
        parallel_backend=parallel_backend,
    )
    result_df.index = result_df["id"]
    assert math.isnan(result_df.loc[0, "clade_fblr_growth_sister"])
    assert result_df.loc[1, "clade_fblr_growth_sister"] < 0
    assert result_df.loc[2, "clade_fblr_growth_sister"] > 0
    assert result_df.loc[3, "clade_fblr_growth_sister"] < 0
    assert result_df.loc[4, "clade_fblr_growth_sister"] > 0
    assert result_df.loc[5, "clade_fblr_growth_sister"] < 0
    assert result_df.loc[6, "clade_fblr_growth_sister"] > 0


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize("parallel_backend", [None, "loky"])
def test_simple6(
    apply: typing.Callable,
    mutate: bool,
    parallel_backend: typing.Optional[str],
):
    # Chain tree: 0
    phylogeny_df = pd.DataFrame(
        {
            "id": [0],
            "ancestor_list": ["[None]"],
            "origin_time": [0],
        },
    )
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_clade_fblr_growth_sister_asexual(
        phylogeny_df,
        mutate=mutate,
        parallel_backend=parallel_backend,
    )
    result_df.index = result_df["id"]
    assert math.isnan(result_df.loc[0, "clade_fblr_growth_sister"])

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize("parallel_backend", [None, "loky"])
def test_simple7(mutate: bool, parallel_backend: typing.Optional[str]):
    # Tree structure:
    #        |---- 4
    #   |--- 0 --- 3
    #   1
    #   |--- 2
    phylogeny_df = pd.DataFrame(
        {
            "id": [3, 0, 1, 2, 4],
            "ancestor_list": ["[0]", "[1]", "[None]", "[1]", "[0]"],
            "origin_time": [50, 20, 10, 30, 40],
        },
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_clade_fblr_growth_sister_asexual(
        phylogeny_df,
        mutate=mutate,
        parallel_backend=parallel_backend,
        work_mask=[False, True, True, True, False],
    )
    result_df.index = result_df["id"]
    assert math.isnan(result_df.loc[3, "clade_fblr_growth_sister"])
    assert result_df.loc[0, "clade_fblr_growth_sister"] > 0
    assert math.isnan(result_df.loc[1, "clade_fblr_growth_sister"])
    assert result_df.loc[2, "clade_fblr_growth_sister"] < 0
    assert math.isnan(result_df.loc[4, "clade_fblr_growth_sister"])

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize("parallel_backend", [None, "loky"])
def test_simple8(
    apply: typing.Callable,
    mutate: bool,
    parallel_backend: typing.Optional[str],
):
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
    result_df = alifestd_mark_clade_fblr_growth_sister_asexual(
        phylogeny_df,
        mutate=mutate,
        parallel_backend=parallel_backend,
        work_mask=[True, True, True, True, False, False, False],
    )
    result_df.index = result_df["id"]
    assert math.isnan(result_df.loc[0, "clade_fblr_growth_sister"])
    assert result_df.loc[1, "clade_fblr_growth_sister"] < 0
    assert result_df.loc[2, "clade_fblr_growth_sister"] > 0
    assert result_df.loc[3, "clade_fblr_growth_sister"] > 0
    assert math.isnan(result_df.loc[4, "clade_fblr_growth_sister"])
    assert math.isnan(result_df.loc[5, "clade_fblr_growth_sister"])
    assert math.isnan(result_df.loc[6, "clade_fblr_growth_sister"])

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize("parallel_backend", [None, "loky"])
def test_simple9(
    apply: typing.Callable,
    mutate: bool,
    parallel_backend: typing.Optional[str],
):
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
            "origin_time": [0, 10, 200, 30, 40, 50, 60],
        },
    )
    phylogeny_df = apply(phylogeny_df)
    phylogeny_df.copy()
    result_df = alifestd_mark_clade_fblr_growth_sister_asexual(
        phylogeny_df,
        mutate=mutate,
        parallel_backend=parallel_backend,
        work_mask=[False, False, True, True, True, False, False],
    )
    result_df.index = result_df["id"]
    assert math.isnan(result_df.loc[0, "clade_fblr_growth_sister"])
    assert math.isnan(result_df.loc[1, "clade_fblr_growth_sister"])
    assert result_df.loc[2, "clade_fblr_growth_sister"] > 0
    assert result_df.loc[3, "clade_fblr_growth_sister"] < 0
    assert result_df.loc[4, "clade_fblr_growth_sister"] > 0
    assert math.isnan(result_df.loc[5, "clade_fblr_growth_sister"])
    assert math.isnan(result_df.loc[6, "clade_fblr_growth_sister"])


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
@pytest.mark.parametrize("parallel_backend", [None, "loky"])
def test_fuzz(
    phylogeny_df: pd.DataFrame, parallel_backend: typing.Optional[str]
):
    if "origin_time" not in phylogeny_df.columns:
        phylogeny_df["origin_time"] = phylogeny_df["id"]

    phylogeny_df = alifestd_join_roots(phylogeny_df)
    phylogeny_df = alifestd_splay_polytomies(phylogeny_df)
    phylogeny_df = alifestd_collapse_unifurcations(phylogeny_df)
    phylogeny_df = alifestd_delete_unifurcating_roots_asexual(phylogeny_df)
    original = phylogeny_df.copy()

    result_df = alifestd_mark_clade_fblr_growth_sister_asexual(
        phylogeny_df, parallel_backend=parallel_backend
    )

    # Confirm that the input dataframe is not mutated.
    assert original.equals(phylogeny_df)

    # Verify result_df
    assert "clade_fblr_growth_sister" in result_df.columns
    assert len(result_df) == len(phylogeny_df)

    assert (
        result_df["clade_fblr_growth_sister"].isna() == result_df["is_root"]
    ).all()
