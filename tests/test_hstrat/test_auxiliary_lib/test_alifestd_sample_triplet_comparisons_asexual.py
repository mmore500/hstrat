import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_make_ancestor_list_col,
    alifestd_make_empty,
    alifestd_sample_triplet_comparisons_asexual,
)


def test_empty():
    with pytest.raises(ValueError):
        alifestd_sample_triplet_comparisons_asexual(
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
        with pytest.raises(ValueError):
            alifestd_sample_triplet_comparisons_asexual(
                xdf, xdf.sample(frac=1), "taxon_label"
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
        info_df = alifestd_sample_triplet_comparisons_asexual(
            adf, bdf, "taxon_label"
        )
        assert info_df["triplet match, lax"].all()
        assert info_df["triplet match, lax/strict"].all()
        assert info_df["triplet match, strict"].all()
        assert info_df["triplet match, strict/lax"].all()
        assert set(df.columns) < set(info_df.columns)


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
    info_df = alifestd_sample_triplet_comparisons_asexual(
        adf, bdf, "taxon_label", n=200
    )
    assert len(info_df) == 200
    assert not info_df["triplet match, lax"].all()
    assert not info_df["triplet match, lax/strict"].all()
    assert not info_df["triplet match, strict"].all()
    assert not info_df["triplet match, strict/lax"].all()
    assert set(adf.columns) < set(info_df.columns)


def test_differing_polytomy():
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
    info_df = alifestd_sample_triplet_comparisons_asexual(
        adf, bdf, "id", n=200
    )
    assert info_df["triplet match, lax"].all()
    assert not info_df["triplet match, lax/strict"].all()
    assert not info_df["triplet match, strict"].all()
    assert info_df["triplet match, strict/lax"].all()
    assert set(adf.columns) < set(info_df.columns)
