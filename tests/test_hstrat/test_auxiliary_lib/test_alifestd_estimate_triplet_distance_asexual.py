import functools
import itertools as it
import typing

import numpy as np
import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_estimate_triplet_distance_asexual,
    alifestd_make_ancestor_list_col,
    alifestd_make_empty,
    alifestd_to_working_format,
    alifestd_validate,
)


def test_empty():
    assert 0.0 == alifestd_estimate_triplet_distance_asexual(
        alifestd_make_empty(), alifestd_make_empty(), "id"
    )


def test_undersize():
    df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "taxon_label": [4, 5, 6],
            "ancestor_id": [0, 0, 0],
        },
    )
    df["ancestor_list"] = alifestd_make_ancestor_list_col(
        df["id"], df["ancestor_id"]
    )
    for xdf in df[:1], df[:2], df:
        assert (
            alifestd_estimate_triplet_distance_asexual(
                xdf, xdf.sample(frac=1), "taxon_label", detail=False
            )
            == 0.0
        )


@pytest.mark.parametrize(
    "df",
    [
        pd.DataFrame(
            {
                "id": [1, 2, 3],
                "taxon_label": ["a", "b", "c"],
                "ancestor_id": [1, 1, 1],
            },
        ),
        pd.DataFrame(
            {
                "id": [0, 1, 2, 3],
                "taxon_label": [0, 1, 2, 3],
                "ancestor_id": [0, 0, 0, 0],
            },
        ),
        pd.DataFrame(
            {
                "id": [0, 1, 2, 3, 4, 5],
                "taxon_label": ["0", "1", "2", "3", "4", "5"],
                "ancestor_id": [0, 0, 0, 0, 1, 2],
            },
        ),
        pd.DataFrame(
            {
                "id": [9, 1, 2, 3, 4, 5],
                "taxon_label": ["9", "1", "2", "3", "4", "5"],
                "ancestor_id": [9, 9, 9, 9, 1, 2],
            },
        ),
        pd.DataFrame(
            {
                "id": [0, 1, 2, 3, 4, 5, 6],
                "taxon_label": ["0", "1", "2", "3", "4", "5", "6"],
                "ancestor_id": [0, 0, 0, 0, 1, 2, 3],
            },
        ),
    ],
)
def test_polytomy_identical(df: pd.DataFrame):
    df["ancestor_list"] = alifestd_make_ancestor_list_col(
        df["id"], df["ancestor_id"]
    )
    for adf, bdf in (df, df), (df, df.sample(frac=1)):
        est, ci, n = alifestd_estimate_triplet_distance_asexual(
            adf, bdf, "taxon_label", confidence=0.95, detail=True
        )
        assert est == 0
        assert np.isclose(ci[0], 0)
        assert ci[1] >= ci[0]


@pytest.mark.parametrize(
    "strict",
    [
        True,
        False,
        *it.product([True, False], repeat=2),
    ],
)
def test_differing_wrong1(
    strict: typing.Union[bool, typing.Tuple[bool, bool]]
):
    adf = pd.DataFrame(
        {
            "id": reversed([9, 1, 2, 3, 4, 5]),
            "taxon_label": reversed(["0", "1", "2", "3", "4", "5"]),
            "ancestor_id": reversed([9, 9, 1, 2, 2, 1]),
        },
    )
    adf["ancestor_list"] = alifestd_make_ancestor_list_col(
        adf["id"], adf["ancestor_id"]
    )
    bdf = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 5, 4],
            "taxon_label": ["0", "1", "2", "3", "5", "4"],
            "ancestor_id": [0, 0, 1, 2, 2, 1],
        },
    )
    bdf["ancestor_list"] = alifestd_make_ancestor_list_col(
        bdf["id"], bdf["ancestor_id"]
    )
    est = alifestd_estimate_triplet_distance_asexual(
        adf, bdf, "taxon_label", confidence=0.95, strict=strict
    )
    assert 1 == est

    est = alifestd_estimate_triplet_distance_asexual(
        adf, bdf.sample(frac=1), "taxon_label", confidence=0.95, strict=strict
    )
    assert 1 == est


@pytest.mark.parametrize(
    "strict", [True, False, *it.product([True, False], repeat=2)]
)
def test_differing_wrong2(
    strict: typing.Union[bool, typing.Tuple[bool, bool]]
):
    adf = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5],
            "taxon_label": ["0", "1", "2", "3", "4", "5"],
            "ancestor_id": [0, 0, 1, 2, 2, 1],
        },
    )
    adf["ancestor_list"] = alifestd_make_ancestor_list_col(
        adf["id"], adf["ancestor_id"]
    )
    bdf = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5],
            "taxon_label": ["0", "1", "2", "3", "4", "5"],
            "ancestor_id": [0, 0, 1, 2, 1, 2],
        },
    )
    bdf["ancestor_list"] = alifestd_make_ancestor_list_col(
        bdf["id"], bdf["ancestor_id"]
    )
    est = alifestd_estimate_triplet_distance_asexual(
        adf, bdf, "taxon_label", confidence=0.95, strict=strict
    )
    assert 1 == est

    est = alifestd_estimate_triplet_distance_asexual(
        adf, bdf.sample(frac=1), "taxon_label", confidence=0.95, strict=strict
    )
    assert 1 == est

    est = alifestd_estimate_triplet_distance_asexual(
        adf.sample(frac=1),
        bdf.sample(frac=1),
        "taxon_label",
        confidence=0.95,
        strict=strict,
    )
    assert 1 == est


@pytest.mark.parametrize("strict", [True, False])
def test_differing_polytomy(strict: bool):
    adf = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5],
            "taxon_label": ["0", "1", "2", "3", "4", "5"],
            "ancestor_id": [0, 0, 1, 2, 2, 1],
        },
    )
    adf["ancestor_list"] = alifestd_make_ancestor_list_col(
        adf["id"], adf["ancestor_id"]
    )
    bdf = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5],
            "taxon_label": ["0", "1", "2", "3", "4", "5"],
            "ancestor_id": [0, 0, 1, 2, 2, 2],
        },
    )
    bdf["ancestor_list"] = alifestd_make_ancestor_list_col(
        bdf["id"], bdf["ancestor_id"]
    )
    est = alifestd_estimate_triplet_distance_asexual(
        adf, bdf, "id", confidence=0.95, precision=0.05, strict=strict
    )
    assert bool(strict) == est

    est = alifestd_estimate_triplet_distance_asexual(
        adf,
        bdf.sample(frac=1),
        "taxon_label",
        confidence=0.95,
        precision=0.05,
        strict=strict,
    )
    assert bool(strict) == est


@pytest.mark.parametrize(
    "strict",
    [
        True,
        False,
        *it.product([True, False], repeat=2),
    ],
)
def test_differing_polytomy2(
    strict: typing.Union[bool, typing.Tuple[bool, bool]]
):
    adf = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6, 7, 8],
            "taxon_label": ["0", "1", "2", "3", "4", "5", "6", "7", "8"],
            "ancestor_id": [0, 0, 1, 2, 2, 1, 3, 3, 2],
        },
    )
    adf["ancestor_list"] = alifestd_make_ancestor_list_col(
        adf["id"], adf["ancestor_id"]
    )
    bdf = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6, 7, 8],
            "taxon_label": ["0", "1", "2", "3", "4", "5", "6", "7", "8"],
            "ancestor_id": [0, 0, 1, 2, 2, 1, 3, 2, 3],
        },
    )
    bdf["ancestor_list"] = alifestd_make_ancestor_list_col(
        bdf["id"], bdf["ancestor_id"]
    )
    est = alifestd_estimate_triplet_distance_asexual(
        adf, bdf, "id", confidence=0.85, precision=0.05, strict=strict
    )
    assert est

    est = alifestd_estimate_triplet_distance_asexual(
        adf,
        bdf.sample(frac=1),
        "taxon_label",
        confidence=0.85,
        precision=0.05,
        strict=strict,
    )
    assert est


@pytest.mark.parametrize(
    "strict",
    [
        True,
        False,
        *it.product([True, False], repeat=2),
    ],
)
def test_identical_polytomy1(
    strict: typing.Union[bool, typing.Tuple[bool, bool]]
):
    adf = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6, 7, 8],
            "taxon_label": ["0", "1", "2", "3", "4", "5", "6", "7", "8"],
            "ancestor_id": [0, 0, 1, 2, 2, 1, 3, 3, 2],
        },
    )
    adf["ancestor_list"] = alifestd_make_ancestor_list_col(
        adf["id"], adf["ancestor_id"]
    )
    bdf = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6, 7, 8],
            "taxon_label": ["0", "1", "2", "3", "4", "5", "6", "7", "8"],
            "ancestor_id": [0, 0, 1, 2, 2, 1, 3, 3, 2],
        },
    )
    bdf["ancestor_list"] = alifestd_make_ancestor_list_col(
        bdf["id"], bdf["ancestor_id"]
    )
    est = alifestd_estimate_triplet_distance_asexual(
        adf, bdf, "id", confidence=0.95, precision=0.05, strict=strict
    )
    assert not est

    est = alifestd_estimate_triplet_distance_asexual(
        adf,
        bdf.sample(frac=1),
        "taxon_label",
        confidence=0.85,
        precision=0.05,
        strict=strict,
    )
    assert not est


@pytest.mark.parametrize(
    "strict",
    [
        True,
        False,
        *it.product([True, False], repeat=2),
    ],
)
def test_differing_wrong_big(
    strict: typing.Union[bool, typing.Tuple[bool, bool]]
):
    adf = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            "taxon_label": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            "ancestor_id": [0, 0, 1, 2, 2, 1, 5, 5, 4, 4],
        },
    )
    adf["ancestor_list"] = alifestd_make_ancestor_list_col(
        adf["id"], adf["ancestor_id"]
    )
    bdf = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            "taxon_label": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            "ancestor_id": [0, 0, 1, 5, 2, 1, 2, 5, 4, 4],
        },
    )
    bdf["ancestor_list"] = alifestd_make_ancestor_list_col(
        bdf["id"], bdf["ancestor_id"]
    )
    est = alifestd_estimate_triplet_distance_asexual(
        adf,
        bdf,
        "taxon_label",
        confidence=0.95,
        precision=0.05,
        strict=strict,
    )
    assert 0 < est < 1

    est = alifestd_estimate_triplet_distance_asexual(
        adf,
        bdf.sample(frac=1),
        "taxon_label",
        confidence=0.95,
        precision=0.05,
        strict=strict,
    )
    assert 0 < est < 1


def test_differing_polytomy_asymmetrical_strict():
    adf = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5],
            "taxon_label": ["0", "1", "2", "3", "4", "5"],
            "ancestor_id": [0, 0, 1, 2, 2, 1],
        },
    )
    adf["ancestor_list"] = alifestd_make_ancestor_list_col(
        adf["id"], adf["ancestor_id"]
    )
    bdf = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5],
            "taxon_label": ["0", "1", "2", "3", "4", "5"],
            "ancestor_id": [0, 0, 1, 2, 2, 2],
        },
    )
    bdf["ancestor_list"] = alifestd_make_ancestor_list_col(
        bdf["id"], bdf["ancestor_id"]
    )
    assert not alifestd_estimate_triplet_distance_asexual(
        adf, bdf, "id", confidence=0.95, precision=0.05, strict=(True, False)
    )
    assert alifestd_estimate_triplet_distance_asexual(
        adf, bdf, "id", confidence=0.95, precision=0.05, strict=(False, True)
    )

    assert alifestd_estimate_triplet_distance_asexual(
        adf,
        bdf.sample(frac=1),
        "taxon_label",
        confidence=0.95,
        precision=0.05,
        strict=(True, True),
    )

    assert not alifestd_estimate_triplet_distance_asexual(
        adf,
        bdf.sample(frac=1),
        "taxon_label",
        confidence=0.95,
        precision=0.05,
        strict=(False, False),
    )


@functools.lru_cache
def make_ref_df(working_format: bool) -> pd.DataFrame:
    #        |
    #      __|_
    #    __|_ |
    #  __|_ | |
    # _|_ | | |
    # | | | | |
    # A B C D E
    ref_df = pd.DataFrame.from_records(
        [
            {"id": 0, "taxon_label": "A", "ancestor_id": 5},
            {"id": 1, "taxon_label": "B", "ancestor_id": 5},
            {"id": 2, "taxon_label": "C", "ancestor_id": 6},
            {"id": 3, "taxon_label": "D", "ancestor_id": 7},
            {"id": 4, "taxon_label": "E", "ancestor_id": 8},
            {"id": 5, "taxon_label": "AB", "ancestor_id": 6},
            {"id": 6, "taxon_label": "ABC", "ancestor_id": 7},
            {"id": 7, "taxon_label": "ABCD", "ancestor_id": 8},
            {"id": 8, "taxon_label": "ABCDE", "ancestor_id": 8},
        ]
    )
    ref_df["ancestor_list"] = alifestd_make_ancestor_list_col(
        ref_df["id"], ref_df["ancestor_id"]
    )
    if working_format:
        ref_df = alifestd_to_working_format(ref_df)

    assert alifestd_validate(ref_df)
    assert not alifestd_estimate_triplet_distance_asexual(
        ref_df,
        ref_df.sample(frac=1),
        "taxon_label",
        confidence=0.85,
        precision=0.05,
        strict=True,
    )
    return ref_df


@functools.lru_cache
def make_swap_df(working_format: bool) -> pd.DataFrame:
    #       |
    #    ___|__
    #  __|__  |
    # _|_ _|_ |
    # | | | | |
    # * B C D E
    # A
    swap_df = pd.DataFrame.from_records(
        [
            {"id": 0, "taxon_label": "A", "ancestor_id": 9},
            {"id": 1, "taxon_label": "B", "ancestor_id": 5},
            {"id": 2, "taxon_label": "C", "ancestor_id": 6},
            {"id": 3, "taxon_label": "D", "ancestor_id": 6},
            {"id": 4, "taxon_label": "E", "ancestor_id": 8},
            {"id": 5, "taxon_label": "AB", "ancestor_id": 7},
            {"id": 6, "taxon_label": "CD", "ancestor_id": 7},
            {"id": 7, "taxon_label": "ABCD", "ancestor_id": 8},
            {"id": 8, "taxon_label": "ABCDE", "ancestor_id": 8},
            {"id": 9, "taxon_label": "A*", "ancestor_id": 5},
        ]
    )
    swap_df["ancestor_list"] = alifestd_make_ancestor_list_col(
        swap_df["id"], swap_df["ancestor_id"]
    )
    if working_format:
        swap_df = alifestd_to_working_format(swap_df)

    assert alifestd_validate(swap_df)
    assert not alifestd_estimate_triplet_distance_asexual(
        swap_df,
        swap_df.sample(frac=1),
        "taxon_label",
        confidence=0.85,
        precision=0.05,
        strict=True,
    )
    return swap_df


@functools.lru_cache
def make_polytomy_df(working_format: bool) -> pd.DataFrame:
    #       |
    #     __|__
    #  ___|__ |
    # _|_ | | |
    # | | | | |
    # A B C D E
    polytomy_df = pd.DataFrame.from_records(
        [
            {"id": 0, "taxon_label": "A", "ancestor_id": 5},
            {"id": 1, "taxon_label": "B", "ancestor_id": 5},
            {"id": 2, "taxon_label": "C", "ancestor_id": 7},
            {"id": 3, "taxon_label": "D", "ancestor_id": 7},
            {"id": 4, "taxon_label": "E", "ancestor_id": 8},
            {"id": 5, "taxon_label": "AB", "ancestor_id": 7},
            {"id": 7, "taxon_label": "ABCD", "ancestor_id": 8},
            {"id": 8, "taxon_label": "ABCDE", "ancestor_id": 8},
        ]
    )
    polytomy_df["ancestor_list"] = alifestd_make_ancestor_list_col(
        polytomy_df["id"], polytomy_df["ancestor_id"]
    )
    if working_format:
        polytomy_df = alifestd_to_working_format(polytomy_df)

    assert alifestd_validate(polytomy_df)
    assert not alifestd_estimate_triplet_distance_asexual(
        polytomy_df,
        polytomy_df.sample(frac=1),
        "taxon_label",
        confidence=0.85,
        precision=0.05,
        strict=True,
    )
    return polytomy_df


@pytest.mark.parametrize(
    "strict",
    [
        True,
        False,
        *it.product([True, False], repeat=2),
    ],
)
@pytest.mark.parametrize(
    "working_format", [True, pytest.param(False, marks=pytest.mark.heavy)]
)
def test_sensitivity1(
    strict: typing.Union[bool, typing.Tuple[bool, bool]],
    working_format: bool,
):

    assert alifestd_estimate_triplet_distance_asexual(
        make_ref_df(working_format),
        make_swap_df(working_format),
        "taxon_label",
        confidence=0.85,
        precision=0.05,
        strict=strict,
    )


@pytest.mark.parametrize(
    "strict",
    [
        True,
        (False, True),
    ],
)
@pytest.mark.parametrize(
    "working_format", [True, pytest.param(False, marks=pytest.mark.heavy)]
)
def test_sensitivity2(
    strict: typing.Union[bool, typing.Tuple[bool, bool]],
    working_format: bool,
):
    assert alifestd_estimate_triplet_distance_asexual(
        make_ref_df(working_format),
        make_polytomy_df(working_format),
        "taxon_label",
        confidence=0.85,
        precision=0.05,
        strict=strict,
    )
    assert alifestd_estimate_triplet_distance_asexual(
        make_ref_df(working_format).sample(frac=1),
        make_polytomy_df(working_format).sample(frac=1),
        "taxon_label",
        confidence=0.85,
        precision=0.05,
        strict=strict,
    )


@pytest.mark.parametrize(
    "strict",
    [
        False,
        (True, False),
    ],
)
@pytest.mark.parametrize(
    "working_format", [True, pytest.param(False, marks=pytest.mark.heavy)]
)
def test_sensitivity3(
    strict: typing.Union[bool, typing.Tuple[bool, bool]],
    working_format: bool,
):
    assert not alifestd_estimate_triplet_distance_asexual(
        make_ref_df(working_format),
        make_polytomy_df(working_format),
        "taxon_label",
        confidence=0.85,
        precision=0.05,
        strict=strict,
    )


@pytest.mark.parametrize(
    "strict",
    [
        True,
        (False, True),
    ],
)
@pytest.mark.parametrize(
    "working_format", [True, pytest.param(False, marks=pytest.mark.heavy)]
)
def test_sensitivity4(
    strict: typing.Union[bool, typing.Tuple[bool, bool]],
    working_format: bool,
):
    assert alifestd_estimate_triplet_distance_asexual(
        make_swap_df(working_format),
        make_polytomy_df(working_format),
        "taxon_label",
        confidence=0.85,
        precision=0.05,
        strict=strict,
    )


@pytest.mark.parametrize(
    "strict",
    [
        False,
        (False, True),
    ],
)
@pytest.mark.parametrize(
    "working_format", [True, pytest.param(False, marks=pytest.mark.heavy)]
)
def test_sensitivity5(
    strict: typing.Union[bool, typing.Tuple[bool, bool]],
    working_format: bool,
):
    assert not alifestd_estimate_triplet_distance_asexual(
        make_polytomy_df(working_format),
        make_swap_df(working_format),
        "taxon_label",
        confidence=0.85,
        precision=0.05,
        strict=strict,
    )
