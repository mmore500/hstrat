import os

import numpy as np
import polars as pl
import pytest

from hstrat._auxiliary_lib import (
    alifestd_from_newick,
    alifestd_from_newick_polars,
)


def test_empty():
    result = alifestd_from_newick_polars("")
    assert len(result) == 0
    assert "id" in result.columns
    assert "ancestor_list" in result.columns
    assert "ancestor_id" in result.columns
    assert "taxon_label" in result.columns
    assert "origin_time_delta" in result.columns
    assert "branch_length" in result.columns


def test_just_root():
    result = alifestd_from_newick_polars("root;")
    assert len(result) == 1
    assert result["id"][0] == 0
    assert result["ancestor_id"][0] == 0
    assert result["taxon_label"][0] == "root"
    assert result["ancestor_list"][0] == "[none]"


def test_twins():
    result = alifestd_from_newick_polars("(twin1,twin2)root;")
    assert len(result) == 3
    assert isinstance(result, pl.DataFrame)

    root = result.filter(pl.col("taxon_label") == "root")
    twin1 = result.filter(pl.col("taxon_label") == "twin1")
    twin2 = result.filter(pl.col("taxon_label") == "twin2")

    assert twin1["ancestor_id"][0] == root["id"][0]
    assert twin2["ancestor_id"][0] == root["id"][0]


def test_branch_lengths():
    result = alifestd_from_newick_polars("(ant:17,(bat:31,cow:22):7,dog:22);")
    # root + ant + internal + bat + cow + dog = 6
    assert len(result) == 6

    ant = result.filter(pl.col("taxon_label") == "ant")
    assert ant["branch_length"][0] == pytest.approx(17.0)
    assert ant["origin_time_delta"][0] == pytest.approx(17.0)


def test_grandchild():
    result = alifestd_from_newick_polars("((child)parent)root;")
    assert len(result) == 3

    root = result.filter(pl.col("taxon_label") == "root")
    parent = result.filter(pl.col("taxon_label") == "parent")
    child = result.filter(pl.col("taxon_label") == "child")

    assert root["ancestor_id"][0] == root["id"][0]
    assert parent["ancestor_id"][0] == root["id"][0]
    assert child["ancestor_id"][0] == parent["id"][0]


def test_no_branch_length_is_null():
    result = alifestd_from_newick_polars("(A,B)C;")
    assert result["branch_length"].is_nan().sum() == 3


@pytest.mark.parametrize(
    "newick_file",
    [
        "grandchild.newick",
        "grandchild_and_aunt.newick",
        "justroot.newick",
        "onlychild.newick",
        "triplets.newick",
        "twins.newick",
    ],
)
def test_newick_assets(newick_file: str):
    newick_path = os.path.join(
        os.path.dirname(__file__), "..", "assets", newick_file
    )
    newick = open(newick_path).read().strip()
    result = alifestd_from_newick_polars(newick)

    assert isinstance(result, pl.DataFrame)
    assert "id" in result.columns
    assert "ancestor_list" in result.columns
    assert "taxon_label" in result.columns

    # root should have ancestor_id == id
    roots = result.filter(pl.col("ancestor_id") == pl.col("id"))
    assert len(roots) >= 1


def test_matches_pandas():
    """Verify polars output matches pandas output."""
    newick = "(ant:17,(bat:31,cow:22):7,dog:22,(elk:33,fox:12):40);"
    pd_result = alifestd_from_newick(newick)
    pl_result = alifestd_from_newick_polars(newick)

    assert len(pd_result) == len(pl_result)

    for col in ["id", "ancestor_id", "taxon_label", "ancestor_list"]:
        assert list(pd_result[col]) == pl_result[col].to_list()

    # compare branch lengths (with nan handling)
    pd_bl = pd_result["branch_length"].tolist()
    pl_bl = pl_result["branch_length"].to_list()
    for a, b in zip(pd_bl, pl_bl):
        if a != a:  # nan check
            assert b != b
        else:
            assert a == pytest.approx(b)


def test_column_dtypes():
    result = alifestd_from_newick_polars("(A:1,B:2)C;")
    assert result["id"].dtype == pl.Int64
    assert result["ancestor_id"].dtype == pl.Int64
    assert result["taxon_label"].dtype == pl.Utf8
    assert result["ancestor_list"].dtype == pl.Utf8
    assert result["origin_time_delta"].dtype == pl.Float64
    assert result["branch_length"].dtype == pl.Float64
