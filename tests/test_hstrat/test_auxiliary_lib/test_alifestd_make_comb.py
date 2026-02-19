import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_find_leaf_ids,
    alifestd_make_comb,
    alifestd_validate,
)


@pytest.mark.parametrize("n_leaves", [2, 3, 4, 5, 8])
def test_node_count(n_leaves: int):
    """Total node count should be 2*n_leaves - 1."""
    df = alifestd_make_comb(n_leaves)
    assert len(df) == 2 * n_leaves - 1


@pytest.mark.parametrize("n_leaves", [2, 3, 4, 5, 8])
def test_leaf_count(n_leaves: int):
    df = alifestd_make_comb(n_leaves)
    leaf_ids = [*alifestd_find_leaf_ids(df)]
    assert len(leaf_ids) == n_leaves


@pytest.mark.parametrize("n_leaves", [2, 3, 4, 5, 8])
def test_contiguous_ids(n_leaves: int):
    """IDs should be contiguous starting from 0."""
    df = alifestd_make_comb(n_leaves)
    assert list(df["id"]) == list(range(len(df)))


@pytest.mark.parametrize("n_leaves", [2, 3, 4, 5, 8])
def test_validates(n_leaves: int):
    df = alifestd_make_comb(n_leaves)
    assert alifestd_validate(df)


@pytest.mark.parametrize("n_leaves", [2, 3, 4, 5, 8])
def test_bifurcating_structure(n_leaves: int):
    """Every internal node should have exactly 2 children."""
    df = alifestd_make_comb(n_leaves)
    leaf_ids = set(alifestd_find_leaf_ids(df))
    for _, row in df.iterrows():
        if row["id"] not in leaf_ids:
            children = df[df["ancestor_list"] == f"[{row['id']}]"]
            assert len(children) == 2


@pytest.mark.parametrize("n_leaves", [2, 3, 4, 5, 8])
def test_topological_sorting(n_leaves: int):
    """Parents should appear before children (topologically sorted)."""
    df = alifestd_make_comb(n_leaves)
    seen = set()
    for _, row in df.iterrows():
        if row["ancestor_list"] != "[None]":
            parent_id = int(row["ancestor_list"].strip("[]"))
            assert parent_id in seen
        seen.add(row["id"])


@pytest.mark.parametrize("n_leaves", [2, 3, 4, 5])
def test_returns_dataframe(n_leaves: int):
    result = alifestd_make_comb(n_leaves)
    assert isinstance(result, pd.DataFrame)
    assert "id" in result.columns
    assert "ancestor_list" in result.columns


@pytest.mark.parametrize("n_leaves", [3, 4, 5])
def test_comb_shape(n_leaves: int):
    """The comb tree should have a chain of internal nodes on one side."""
    df = alifestd_make_comb(n_leaves)
    leaf_ids = set(alifestd_find_leaf_ids(df))
    # Internal nodes should form a chain: 0, 2, 4, ...
    internal_ids = [
        row["id"] for _, row in df.iterrows() if row["id"] not in leaf_ids
    ]
    assert internal_ids == list(range(0, 2 * (n_leaves - 1), 2))
