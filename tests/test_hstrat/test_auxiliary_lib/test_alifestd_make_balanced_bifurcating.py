import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_find_leaf_ids,
    alifestd_make_balanced_bifurcating,
    alifestd_validate,
)


@pytest.mark.parametrize("depth", [1, 2, 3, 4, 5])
def test_node_count(depth: int):
    """Total node count should be 2^depth - 1."""
    df = alifestd_make_balanced_bifurcating(depth)
    assert len(df) == 2**depth - 1


@pytest.mark.parametrize("depth", [2, 3, 4, 5])
def test_leaf_count(depth: int):
    """Leaf count should be 2^(depth-1)."""
    df = alifestd_make_balanced_bifurcating(depth)
    leaf_ids = [*alifestd_find_leaf_ids(df)]
    assert len(leaf_ids) == 2 ** (depth - 1)


@pytest.mark.parametrize("depth", [1, 2, 3, 4, 5])
def test_contiguous_ids(depth: int):
    """IDs should be contiguous starting from 0."""
    df = alifestd_make_balanced_bifurcating(depth)
    assert list(df["id"]) == list(range(len(df)))


@pytest.mark.parametrize("depth", [1, 2, 3, 4, 5])
def test_validates(depth: int):
    df = alifestd_make_balanced_bifurcating(depth)
    assert alifestd_validate(df)


@pytest.mark.parametrize("depth", [2, 3, 4, 5])
def test_bifurcating_structure(depth: int):
    """Every internal node should have exactly 2 children."""
    df = alifestd_make_balanced_bifurcating(depth)
    leaf_ids = set(alifestd_find_leaf_ids(df))
    for _, row in df.iterrows():
        if row["id"] not in leaf_ids:
            children = df[df["ancestor_list"] == f"[{row['id']}]"]
            assert len(children) == 2


def test_single_root():
    """depth=1 should produce a single root node."""
    df = alifestd_make_balanced_bifurcating(1)
    assert len(df) == 1
    assert df.iloc[0]["ancestor_list"] == "[None]"


@pytest.mark.parametrize("depth", [1, 2, 3, 4, 5])
def test_topological_sorting(depth: int):
    """Parents should appear before children (topologically sorted)."""
    df = alifestd_make_balanced_bifurcating(depth)
    seen = set()
    for _, row in df.iterrows():
        if row["ancestor_list"] != "[None]":
            parent_id = int(row["ancestor_list"].strip("[]"))
            assert parent_id in seen
        seen.add(row["id"])


@pytest.mark.parametrize("depth", [1, 2, 3, 4])
def test_returns_dataframe(depth: int):
    result = alifestd_make_balanced_bifurcating(depth)
    assert isinstance(result, pd.DataFrame)
    assert "id" in result.columns
    assert "ancestor_list" in result.columns
