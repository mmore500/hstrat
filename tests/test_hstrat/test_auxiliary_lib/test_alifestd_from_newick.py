import os

import numpy as np
import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_as_newick_asexual,
    alifestd_from_newick,
    alifestd_make_empty,
    alifestd_try_add_ancestor_id_col,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


def test_empty():
    result = alifestd_from_newick("")
    assert len(result) == 0
    assert "id" in result.columns
    assert "ancestor_list" in result.columns
    assert "ancestor_id" in result.columns
    assert "taxon_label" in result.columns
    assert "origin_time_delta" in result.columns
    assert "branch_length" in result.columns


def test_just_root():
    result = alifestd_from_newick("root;")
    assert len(result) == 1
    assert result["id"].iloc[0] == 0
    assert result["ancestor_id"].iloc[0] == 0  # root is own ancestor
    assert result["taxon_label"].iloc[0] == "root"
    assert result["ancestor_list"].iloc[0] == "[none]"


def test_just_root_no_label():
    result = alifestd_from_newick(";")
    assert len(result) == 1
    assert result["id"].iloc[0] == 0
    assert result["ancestor_id"].iloc[0] == 0
    assert result["taxon_label"].iloc[0] == ""


def test_onlychild():
    result = alifestd_from_newick("(child)root;")
    assert len(result) == 2

    root = result[result["taxon_label"] == "root"]
    child = result[result["taxon_label"] == "child"]

    assert len(root) == 1
    assert len(child) == 1
    assert root["ancestor_id"].iloc[0] == root["id"].iloc[0]
    assert child["ancestor_id"].iloc[0] == root["id"].iloc[0]


def test_twins():
    result = alifestd_from_newick("(twin1,twin2)root;")
    assert len(result) == 3

    root = result[result["taxon_label"] == "root"]
    twin1 = result[result["taxon_label"] == "twin1"]
    twin2 = result[result["taxon_label"] == "twin2"]

    assert len(root) == 1
    assert len(twin1) == 1
    assert len(twin2) == 1
    assert twin1["ancestor_id"].iloc[0] == root["id"].iloc[0]
    assert twin2["ancestor_id"].iloc[0] == root["id"].iloc[0]


def test_triplets():
    result = alifestd_from_newick("(triplet1,triplet2,triplet3)root;")
    assert len(result) == 4

    root = result[result["taxon_label"] == "root"]
    for name in ["triplet1", "triplet2", "triplet3"]:
        child = result[result["taxon_label"] == name]
        assert len(child) == 1
        assert child["ancestor_id"].iloc[0] == root["id"].iloc[0]


def test_grandchild():
    result = alifestd_from_newick("((child)parent)root;")
    assert len(result) == 3

    root = result[result["taxon_label"] == "root"]
    parent = result[result["taxon_label"] == "parent"]
    child = result[result["taxon_label"] == "child"]

    assert root["ancestor_id"].iloc[0] == root["id"].iloc[0]
    assert parent["ancestor_id"].iloc[0] == root["id"].iloc[0]
    assert child["ancestor_id"].iloc[0] == parent["id"].iloc[0]


def test_grandchild_and_aunt():
    result = alifestd_from_newick("((child)parent,aunt)root;")
    assert len(result) == 4

    root = result[result["taxon_label"] == "root"]
    parent = result[result["taxon_label"] == "parent"]
    child = result[result["taxon_label"] == "child"]
    aunt = result[result["taxon_label"] == "aunt"]

    assert parent["ancestor_id"].iloc[0] == root["id"].iloc[0]
    assert child["ancestor_id"].iloc[0] == parent["id"].iloc[0]
    assert aunt["ancestor_id"].iloc[0] == root["id"].iloc[0]


def test_branch_lengths():
    result = alifestd_from_newick("(ant:17,(bat:31,cow:22):7,dog:22);")
    # root + ant + internal + bat + cow + dog = 6 nodes
    assert len(result) == 6

    ant = result[result["taxon_label"] == "ant"]
    bat = result[result["taxon_label"] == "bat"]
    cow = result[result["taxon_label"] == "cow"]
    dog = result[result["taxon_label"] == "dog"]

    assert ant["branch_length"].iloc[0] == pytest.approx(17.0)
    assert bat["branch_length"].iloc[0] == pytest.approx(31.0)
    assert cow["branch_length"].iloc[0] == pytest.approx(22.0)
    assert dog["branch_length"].iloc[0] == pytest.approx(22.0)

    # internal node with branch length 7
    internal = result[
        (result["taxon_label"] == "")
        & (result["ancestor_id"] != result["id"])
    ]
    assert len(internal) == 1
    assert internal["branch_length"].iloc[0] == pytest.approx(7.0)

    # origin_time_delta matches branch_length
    assert (
        result["origin_time_delta"].dropna()
        == result["branch_length"].dropna()
    ).all()


def test_branch_lengths_float():
    result = alifestd_from_newick("(A:0.1,B:0.2,(C:0.3,D:0.4):0.5);")
    a = result[result["taxon_label"] == "A"]
    b = result[result["taxon_label"] == "B"]
    c = result[result["taxon_label"] == "C"]
    d = result[result["taxon_label"] == "D"]

    assert a["branch_length"].iloc[0] == pytest.approx(0.1)
    assert b["branch_length"].iloc[0] == pytest.approx(0.2)
    assert c["branch_length"].iloc[0] == pytest.approx(0.3)
    assert d["branch_length"].iloc[0] == pytest.approx(0.4)


def test_no_branch_length_is_nan():
    result = alifestd_from_newick("(A,B)C;")
    assert np.isnan(result["branch_length"].iloc[0])  # root C
    assert np.isnan(result["branch_length"].iloc[1])  # A
    assert np.isnan(result["branch_length"].iloc[2])  # B


def test_mixed_branch_lengths():
    result = alifestd_from_newick("(A:5,B)C;")
    a = result[result["taxon_label"] == "A"]
    b = result[result["taxon_label"] == "B"]
    assert a["branch_length"].iloc[0] == pytest.approx(5.0)
    assert np.isnan(b["branch_length"].iloc[0])


def test_ancestor_list_col():
    result = alifestd_from_newick("(A,B)C;")
    root = result[result["taxon_label"] == "C"]
    a = result[result["taxon_label"] == "A"]
    b = result[result["taxon_label"] == "B"]

    assert root["ancestor_list"].iloc[0] == "[none]"
    assert a["ancestor_list"].iloc[0] == f"[{root['id'].iloc[0]}]"
    assert b["ancestor_list"].iloc[0] == f"[{root['id'].iloc[0]}]"


def test_example_newick():
    newick = "(ant:17, (bat:31, cow:22):7, dog:22, (elk:33, fox:12):40);"
    result = alifestd_from_newick(newick)
    # root + ant + internal1 + bat + cow + dog + internal2 + elk + fox = 9
    assert len(result) == 9

    fox = result[result["taxon_label"] == "fox"]
    assert fox["branch_length"].iloc[0] == pytest.approx(12.0)

    elk = result[result["taxon_label"] == "elk"]
    assert elk["branch_length"].iloc[0] == pytest.approx(33.0)


def test_quoted_labels():
    result = alifestd_from_newick("('node A','node B')'root node';")
    assert len(result) == 3
    labels = set(result["taxon_label"])
    assert "node A" in labels
    assert "node B" in labels
    assert "root node" in labels


def test_contiguous_ids():
    result = alifestd_from_newick(
        "(((grandchild1, grandchild2)triplet1,triplet2,triplet3)parent,aunt,uncle)root;"
    )
    assert list(result["id"]) == list(range(len(result)))


@pytest.mark.parametrize(
    "newick_file",
    [
        "grandchild.newick",
        "grandchild_and_aunt.newick",
        "grandchild_and_auntuncle.newick",
        "grandtriplets.newick",
        "grandtriplets_and_aunt.newick",
        "grandtriplets_and_auntuncle.newick",
        "grandtwins.newick",
        "grandtwins_and_aunt.newick",
        "grandtwins_and_auntuncle.newick",
        "greatgrandtwins_and_auntuncle.newick",
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
    result = alifestd_from_newick(newick)

    assert "id" in result.columns
    assert "ancestor_list" in result.columns
    assert "ancestor_id" in result.columns
    assert "taxon_label" in result.columns

    # root should have ancestor_id == id
    roots = result[result["ancestor_id"] == result["id"]]
    assert len(roots) >= 1

    # all non-root ancestor_ids should reference valid ids
    non_root = result[result["ancestor_id"] != result["id"]]
    assert non_root["ancestor_id"].isin(result["id"]).all()


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
def test_roundtrip(phylogeny_df: pd.DataFrame):
    """Test roundtrip: alife -> newick -> alife preserves topology."""
    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df)

    newick = alifestd_as_newick_asexual(phylogeny_df, taxon_label="id")
    reconstructed = alifestd_from_newick(newick)

    assert len(reconstructed) == len(phylogeny_df)

    # build parent mapping from reconstructed data using taxon_labels as ids
    taxon_labels = dict(
        zip(reconstructed["id"], reconstructed["taxon_label"])
    )
    reconstructed_edges = set()
    for _, row in reconstructed.iterrows():
        child_label = row["taxon_label"]
        if row["ancestor_id"] != row["id"]:
            parent_label = taxon_labels[row["ancestor_id"]]
            reconstructed_edges.add((int(child_label), int(parent_label)))
        else:
            reconstructed_edges.add((int(child_label), int(child_label)))

    original_edges = set()
    for _, row in phylogeny_df.iterrows():
        original_edges.add((int(row["id"]), int(row["ancestor_id"])))

    assert reconstructed_edges == original_edges


def test_whitespace_handling():
    result1 = alifestd_from_newick("(A,B)C;")
    result2 = alifestd_from_newick("  (A,B)C;  ")
    assert len(result1) == len(result2)
    assert list(result1["taxon_label"]) == list(result2["taxon_label"])


def test_comments_ignored():
    result = alifestd_from_newick("(A[comment],B)C;")
    assert len(result) == 3
    labels = set(result["taxon_label"])
    assert "A" in labels
    assert "B" in labels
    assert "C" in labels


def test_negative_branch_length():
    result = alifestd_from_newick("(A:-1.5,B:2.0);")
    a = result[result["taxon_label"] == "A"]
    assert a["branch_length"].iloc[0] == pytest.approx(-1.5)


def test_scientific_notation():
    result = alifestd_from_newick("(A:1.5e-3,B:2E4);")
    a = result[result["taxon_label"] == "A"]
    b = result[result["taxon_label"] == "B"]
    assert a["branch_length"].iloc[0] == pytest.approx(1.5e-3)
    assert b["branch_length"].iloc[0] == pytest.approx(2e4)
