import os

import alifedata_phyloinformatics_convert as apc
import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_as_newick_asexual,
    alifestd_make_empty,
    alifestd_try_add_ancestor_id_col,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


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
def test_fuzz(phylogeny_df: pd.DataFrame):
    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df)
    original = phylogeny_df.copy()

    result = alifestd_as_newick_asexual(phylogeny_df, taxon_label="id")
    assert original.equals(phylogeny_df)

    rosetta_tree = apc.RosettaTree.from_newick(result)
    reconstructed = rosetta_tree.as_alife
    reconstructed["taxon_label"].fillna(reconstructed["label"], inplace=True)
    reconstructed["taxon_label"] = reconstructed["taxon_label"].astype(int)
    reconstructed = alifestd_try_add_ancestor_id_col(reconstructed)

    assert len(reconstructed) == len(original)

    taxon_labels = dict(zip(reconstructed["id"], reconstructed["taxon_label"]))
    assert set(zip(original["id"], original["ancestor_id"])) == set(
        zip(
            reconstructed["taxon_label"],
            reconstructed["ancestor_id"].map(taxon_labels),
        )
    ), (original, result, rosetta_tree.as_newick)


def test_empty():
    res = alifestd_as_newick_asexual(alifestd_make_empty())
    assert res == ";"


@pytest.mark.parametrize("mutate", [True, False])
def test_simple1(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[1]"],
            "origin_time_delta": [3.1, 4.0, 1.0],
        },
    )
    original_df = phylogeny_df.copy()
    result = alifestd_as_newick_asexual(
        phylogeny_df,
        taxon_label=None,
        mutate=mutate,
    )
    assert result == "((:1):4):3.1;"

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple2(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [3, 0, 1, 2],
            "ancestor_list": ["[0]", "[1]", "[None]", "[1]"],
        },
    )
    original_df = phylogeny_df.copy()
    result = alifestd_as_newick_asexual(
        phylogeny_df,
        taxon_label=None,
        mutate=mutate,
    )
    assert result == "(,());"

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple3(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [4, 0, 2, 3],
            "ancestor_list": ["[None]", "[None]", "[0]", "[4]"],
            "label": ["A", "B", "C", "D"],
        },
    )
    original_df = phylogeny_df.copy()
    result = alifestd_as_newick_asexual(
        phylogeny_df,
        taxon_label="label",
        mutate=mutate,
    )
    assert result == "(D)A;\n(C)B;"

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple4(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_list": ["[None]", "[0]", "[0]", "[1]", "[0]"],
            "origin_time": [0, 1, 2, 5, 90],
        },
    )
    original_df = phylogeny_df.copy()
    result = alifestd_as_newick_asexual(
        phylogeny_df,
        mutate=mutate,
        taxon_label="id",
    )

    assert result == "(4:90,2:2,(3:4)1:1)0:0;"

    if not mutate:
        assert original_df.equals(phylogeny_df)
