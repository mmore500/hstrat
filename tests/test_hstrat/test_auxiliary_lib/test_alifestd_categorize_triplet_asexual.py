import pandas as pd

from hstrat._auxiliary_lib import (
    alifestd_categorize_triplet_asexual,
    alifestd_make_ancestor_list_col,
)


def test_polytomy():
    df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "ancestor_id": [1, 1, 1],
        },
    )
    df["ancestor_list"] = alifestd_make_ancestor_list_col(
        df["id"], df["ancestor_id"]
    )
    for xdf in df, df.sample(frac=1), df.sample(frac=1), df.sample(frac=1):
        assert alifestd_categorize_triplet_asexual(xdf, [1, 2, 3]) == -1
        assert alifestd_categorize_triplet_asexual(xdf, [3, 1, 2]) == -1

    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [0, 0, 0, 0],
        },
    )
    df["ancestor_list"] = alifestd_make_ancestor_list_col(
        df["id"], df["ancestor_id"]
    )
    for xdf in df, df.sample(frac=1), df.sample(frac=1), df.sample(frac=1):
        assert alifestd_categorize_triplet_asexual(xdf, [1, 2, 3]) == -1
        assert alifestd_categorize_triplet_asexual(xdf, [3, 1, 2]) == -1

    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5],
            "ancestor_id": [0, 0, 0, 0, 1, 2],
        },
    )
    df["ancestor_list"] = alifestd_make_ancestor_list_col(
        df["id"], df["ancestor_id"]
    )
    for xdf in df, df.sample(frac=1), df.sample(frac=1), df.sample(frac=1):
        assert alifestd_categorize_triplet_asexual(xdf, [3, 4, 5]) == -1
        assert alifestd_categorize_triplet_asexual(xdf, [5, 3, 4]) == -1
        assert alifestd_categorize_triplet_asexual(xdf, [5, 4, 3]) == -1

    df = pd.DataFrame(
        {
            "id": [9, 1, 2, 3, 4, 5],
            "ancestor_id": [9, 9, 9, 9, 1, 2],
        },
    )
    df["ancestor_list"] = alifestd_make_ancestor_list_col(
        df["id"], df["ancestor_id"]
    )
    for xdf in df, df.sample(frac=1), df.sample(frac=1), df.sample(frac=1):
        assert alifestd_categorize_triplet_asexual(xdf, [3, 4, 5]) == -1
        assert alifestd_categorize_triplet_asexual(xdf, [5, 3, 4]) == -1
        assert alifestd_categorize_triplet_asexual(xdf, [5, 4, 3]) == -1

    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_id": [0, 0, 0, 0, 1, 2, 3],
        },
    )
    df["ancestor_list"] = alifestd_make_ancestor_list_col(
        df["id"], df["ancestor_id"]
    )
    for xdf in df, df.sample(frac=1), df.sample(frac=1), df.sample(frac=1):
        assert alifestd_categorize_triplet_asexual(xdf, [6, 4, 5]) == -1
        assert alifestd_categorize_triplet_asexual(xdf, [5, 6, 4]) == -1
        assert alifestd_categorize_triplet_asexual(xdf, [5, 4, 6]) == -1


def test_bifurcating():
    df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "ancestor_id": [1, 1, 2, 2, 1],
        },
    )
    df["ancestor_list"] = alifestd_make_ancestor_list_col(
        df["id"], df["ancestor_id"]
    )
    for xdf in df, df.sample(frac=1), df.sample(frac=1), df.sample(frac=1):
        assert alifestd_categorize_triplet_asexual(xdf, [3, 4, 5]) == 2
        assert alifestd_categorize_triplet_asexual(xdf, [3, 5, 4]) == 1
        assert alifestd_categorize_triplet_asexual(xdf, [5, 3, 4]) == 0

    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5],
            "ancestor_id": [0, 0, 1, 2, 2, 1],
        },
    )
    df["ancestor_list"] = alifestd_make_ancestor_list_col(
        df["id"], df["ancestor_id"]
    )
    for xdf in df, df.sample(frac=1), df.sample(frac=1), df.sample(frac=1):
        assert alifestd_categorize_triplet_asexual(xdf, [3, 4, 5]) == 2
        assert alifestd_categorize_triplet_asexual(xdf, [3, 5, 4]) == 1
        assert alifestd_categorize_triplet_asexual(xdf, [5, 3, 4]) == 0

    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 6, 5, 4],
            "ancestor_id": [0, 0, 1, 2, 2, 1, 6],
        },
    )
    df["ancestor_list"] = alifestd_make_ancestor_list_col(
        df["id"], df["ancestor_id"]
    )
    for xdf in df, df.sample(frac=1), df.sample(frac=1), df.sample(frac=1):
        assert alifestd_categorize_triplet_asexual(xdf, [3, 4, 5]) == 2
        assert alifestd_categorize_triplet_asexual(xdf, [3, 5, 4]) == 1
        assert alifestd_categorize_triplet_asexual(xdf, [5, 3, 4]) == 0

    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5],
            "taxon_label": ["0", "1", "2", "3", "4", "5"],
            "ancestor_id": [0, 0, 1, 2, 1, 2],
        },
    )
    df["ancestor_list"] = alifestd_make_ancestor_list_col(
        df["id"], df["ancestor_id"]
    )
    for xdf in df, df.sample(frac=1), df.sample(frac=1), df.sample(frac=1):
        assert alifestd_categorize_triplet_asexual(xdf, [3, 4, 5]) == 1
        assert alifestd_categorize_triplet_asexual(xdf, [3, 5, 4]) == 2
        assert alifestd_categorize_triplet_asexual(xdf, [4, 3, 5]) == 0
