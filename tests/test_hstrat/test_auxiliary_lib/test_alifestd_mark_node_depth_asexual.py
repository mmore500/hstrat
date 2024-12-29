import os

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_find_leaf_ids,
    alifestd_find_root_ids,
    alifestd_has_multiple_roots,
    alifestd_make_empty,
    alifestd_mark_node_depth_asexual,
    alifestd_validate,
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
    original = phylogeny_df.copy()

    result = alifestd_mark_node_depth_asexual(phylogeny_df)

    assert alifestd_validate(result)
    assert original.equals(phylogeny_df)

    leaf_ids = [*alifestd_find_leaf_ids(phylogeny_df)]
    for leaf_id in leaf_ids:
        node_depth = result[result["id"] == leaf_id]["node_depth"].squeeze()
        assert node_depth > 0

    assert not alifestd_has_multiple_roots(phylogeny_df)
    (root_id,) = alifestd_find_root_ids(phylogeny_df)
    node_depth = result[result["id"] == root_id]["node_depth"].squeeze()
    assert node_depth == 0

    assert all(0 <= result["node_depth"])
    assert all(result["node_depth"] <= len(phylogeny_df))


def test_empty():
    res = alifestd_mark_node_depth_asexual(alifestd_make_empty())
    assert "node_depth" in res
    assert len(res) == 0


@pytest.mark.parametrize("mutate", [True, False])
def test_simple1(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[1]"],
        },
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_node_depth_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    assert result_df.loc[0, "node_depth"] == 0
    assert result_df.loc[1, "node_depth"] == 1
    assert result_df.loc[2, "node_depth"] == 2

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple2(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 0, 2, 3],
            "ancestor_list": ["[0]", "[None]", "[0]", "[1]"],
        },
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_node_depth_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[1, "node_depth"] == 1
    assert result_df.loc[0, "node_depth"] == 0
    assert result_df.loc[2, "node_depth"] == 1
    assert result_df.loc[3, "node_depth"] == 2

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple3(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 0, 2, 3],
            "ancestor_list": ["[None]", "[None]", "[0]", "[1]"],
        },
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_node_depth_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[1, "node_depth"] == 0
    assert result_df.loc[0, "node_depth"] == 0
    assert result_df.loc[2, "node_depth"] == 1
    assert result_df.loc[3, "node_depth"] == 1

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple4(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_list": ["[None]", "[0]", "[0]", "[1]"],
        },
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_node_depth_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[0, "node_depth"] == 0
    assert result_df.loc[1, "node_depth"] == 1
    assert result_df.loc[2, "node_depth"] == 1
    assert result_df.loc[3, "node_depth"] == 2

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple5(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [3, 0, 1, 2],
            "ancestor_list": ["[0]", "[1]", "[None]", "[1]"],
        },
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_node_depth_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[1, "node_depth"] == 0
    assert result_df.loc[0, "node_depth"] == 1
    assert result_df.loc[2, "node_depth"] == 1
    assert result_df.loc[3, "node_depth"] == 2

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple6(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [4, 0, 2, 3],
            "ancestor_list": ["[None]", "[None]", "[0]", "[4]"],
        },
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_node_depth_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[0, "node_depth"] == 0
    assert result_df.loc[2, "node_depth"] == 1
    assert result_df.loc[3, "node_depth"] == 1
    assert result_df.loc[4, "node_depth"] == 0

    if not mutate:
        assert original_df.equals(phylogeny_df)
