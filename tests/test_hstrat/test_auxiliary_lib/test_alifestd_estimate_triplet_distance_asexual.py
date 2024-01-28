import numpy as np
import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_estimate_triplet_distance_asexual,
    alifestd_make_ancestor_list_col,
    alifestd_make_empty,
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


@pytest.mark.parametrize("strict", [True, False])
def test_differing_wrong1(strict: bool):
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


@pytest.mark.parametrize("strict", [False])
def test_differing_wrong2(strict: bool):
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


@pytest.mark.parametrize("strict", [True, False])
def test_differing_wrong_big(strict: bool):
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
