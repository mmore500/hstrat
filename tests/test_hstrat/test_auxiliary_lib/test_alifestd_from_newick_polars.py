import os
import pathlib

import numpy as np
import pandas as pd
import polars as pl
import pytest

from hstrat._auxiliary_lib import (
    alifestd_as_newick_asexual,
    alifestd_from_newick,
    alifestd_from_newick_polars,
    alifestd_try_add_ancestor_id_col,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


def test_empty():
    result = alifestd_from_newick_polars("")
    assert len(result) == 0
    assert "id" in result.columns
    assert "ancestor_list" not in result.columns
    assert "ancestor_id" in result.columns
    assert "taxon_label" in result.columns
    assert "origin_time_delta" in result.columns
    assert "branch_length" in result.columns

    result_with_al = alifestd_from_newick_polars("", create_ancestor_list=True)
    assert "ancestor_list" in result_with_al.columns


def test_just_root():
    result = alifestd_from_newick_polars("root;", create_ancestor_list=True)
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
    newick = pathlib.Path(newick_path).read_text().strip()
    result = alifestd_from_newick_polars(newick, create_ancestor_list=True)

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
    pd_result = alifestd_from_newick(newick, create_ancestor_list=True)
    pl_result = alifestd_from_newick_polars(newick, create_ancestor_list=True)

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
    result = alifestd_from_newick_polars(
        "(A:1,B:2)C;", create_ancestor_list=True
    )
    assert result["id"].dtype == pl.Int64
    assert result["ancestor_id"].dtype == pl.Int64
    assert result["taxon_label"].dtype == pl.Utf8
    assert result["ancestor_list"].dtype == pl.Utf8
    assert result["origin_time_delta"].dtype == pl.Float64
    assert result["branch_length"].dtype == pl.Float64


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
def test_roundtrip(newick_file: str):
    """Test roundtrip: newick -> polars alife -> newick -> polars alife."""
    newick_path = os.path.join(
        os.path.dirname(__file__), "..", "assets", newick_file
    )
    newick = pathlib.Path(newick_path).read_text().strip()
    result = alifestd_from_newick_polars(newick)

    # use pandas variant for alifestd_as_newick_asexual roundtrip
    pd_result = alifestd_from_newick(newick)
    re_newick = alifestd_as_newick_asexual(
        pd_result, taxon_label="taxon_label"
    )
    re_result = alifestd_from_newick_polars(re_newick)
    assert len(re_result) == len(result)


@pytest.mark.parametrize(
    "phylogeny_csv",
    [
        "example-standard-toy-asexual-phylogeny.csv",
        "example-standard-toy-asexual-phylogeny-noncompact1.csv",
        "example-standard-toy-asexual-phylogeny-noncompact2.csv",
        "example-standard-toy-asexual-phylogeny-uniq.csv",
        "nk_ecoeaselection.csv",
        "nk_lexicaseselection.csv",
        "nk_tournamentselection.csv",
        "prunetestphylo.csv",
        "collapse_unifurcations_testphylo.csv",
    ],
)
@pytest.mark.parametrize("taxon_label", [None, "id"])
@pytest.mark.parametrize("with_branch_length", [True, False])
def test_alifestd_asset_roundtrip(
    phylogeny_csv, taxon_label, with_branch_length
):
    """Test roundtrip: alifestd -> newick -> polars alife using assets."""
    phylogeny_df = pd.read_csv(f"{assets_path}/{phylogeny_csv}")
    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df)

    if with_branch_length:
        if (
            "origin_time_delta" not in phylogeny_df.columns
            and "origin_time" not in phylogeny_df.columns
        ):
            phylogeny_df["origin_time_delta"] = np.arange(
                len(phylogeny_df), dtype=float
            )
    else:
        phylogeny_df = phylogeny_df.drop(
            columns=["origin_time", "origin_time_delta"],
            errors="ignore",
        )

    newick = alifestd_as_newick_asexual(
        phylogeny_df,
        taxon_label=taxon_label,
    )
    reconstructed = alifestd_from_newick_polars(newick)

    assert len(reconstructed) == len(phylogeny_df)
    assert isinstance(reconstructed, pl.DataFrame)

    # verify single root
    roots = reconstructed.filter(pl.col("ancestor_id") == pl.col("id"))
    assert len(roots) == 1

    if taxon_label == "id":
        # compare edges using polars column extraction
        id_to_label = dict(
            zip(
                reconstructed["id"].to_list(),
                reconstructed["taxon_label"].to_list(),
            )
        )
        reconstructed_edges = set()
        for rid, raid in zip(
            reconstructed["id"].to_list(),
            reconstructed["ancestor_id"].to_list(),
        ):
            label = id_to_label[rid]
            parent_label = id_to_label[raid]
            reconstructed_edges.add((int(label), int(parent_label)))

        original_edges = set()
        for _, row in phylogeny_df.iterrows():
            original_edges.add((int(row["id"]), int(row["ancestor_id"])))

        assert reconstructed_edges == original_edges

    if with_branch_length:
        # verify branch lengths are present (not all NaN)
        assert reconstructed["branch_length"].is_nan().sum() < len(
            reconstructed
        )
