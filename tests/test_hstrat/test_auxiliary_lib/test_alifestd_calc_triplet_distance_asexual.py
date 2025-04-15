import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_calc_triplet_distance_asexual,
    alifestd_make_ancestor_list_col,
)


@pytest.mark.parametrize(
    "df",
    [
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
        assert alifestd_calc_triplet_distance_asexual(adf, bdf) == 0


def test_differing_wrong1():
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
    assert 0 < alifestd_calc_triplet_distance_asexual(adf, bdf) < 1
    assert (
        0 < alifestd_calc_triplet_distance_asexual(adf, bdf.sample(frac=1)) < 1
    )


def test_differing_wrong2():
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
    assert 0 < alifestd_calc_triplet_distance_asexual(adf, bdf) < 1
    assert (
        0 < alifestd_calc_triplet_distance_asexual(adf, bdf.sample(frac=1)) < 1
    )
    assert (
        0
        < alifestd_calc_triplet_distance_asexual(
            adf.sample(frac=1), bdf.sample(frac=1)
        )
        < 1
    )


def test_identical_polytomy1():
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
    assert alifestd_calc_triplet_distance_asexual(adf, bdf, "taxon_label") == 0
    assert (
        alifestd_calc_triplet_distance_asexual(
            adf, bdf.sample(frac=1), "taxon_label"
        )
        == 0
    )


def test_differing_wrong_big():
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
    est = alifestd_calc_triplet_distance_asexual(
        adf,
        bdf,
        "taxon_label",
    )
    assert 0 < est < 1

    est = alifestd_calc_triplet_distance_asexual(
        adf,
        bdf.sample(frac=1),
        "taxon_label",
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
    assert (
        0 < alifestd_calc_triplet_distance_asexual(adf, bdf, "taxon_label") < 1
    )
    assert (
        0 < alifestd_calc_triplet_distance_asexual(adf, bdf, "taxon_label") < 1
    )
    assert (
        0
        < alifestd_calc_triplet_distance_asexual(
            adf,
            bdf.sample(frac=1),
            "taxon_label",
        )
        < 1
    )
    assert (
        0
        < alifestd_calc_triplet_distance_asexual(
            adf,
            bdf.sample(frac=1),
            "taxon_label",
        )
        < 1
    )
