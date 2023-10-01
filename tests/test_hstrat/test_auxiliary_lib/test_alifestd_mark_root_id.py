import os

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_find_root_ids,
    alifestd_has_multiple_roots,
    alifestd_make_empty,
    alifestd_mark_root_id,
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

    result = alifestd_mark_root_id(phylogeny_df)

    assert alifestd_validate(result)
    assert original.equals(phylogeny_df)

    assert not alifestd_has_multiple_roots(phylogeny_df)
    (root_id,) = alifestd_find_root_ids(phylogeny_df)
    assert all(result["root_id"] == root_id)


def test_empty():
    res = alifestd_mark_root_id(alifestd_make_empty())
    assert "root_id" in res
    assert len(res) == 0


def test_singleton():
    record = {"id": 0, "ancestor_id": 0, "ancestor_list": "[None]"}
    original = pd.DataFrame.from_records([record])

    res = alifestd_mark_root_id(original)
    assert alifestd_validate(res)
    assert res["root_id"].squeeze() == 0

    res = alifestd_mark_root_id(original.drop("ancestor_id", axis=1))
    assert alifestd_validate(res)
    assert res["root_id"].squeeze() == 0


@pytest.mark.parametrize("mutate", [True, False])
def test_asexual1(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [42, 1, 2],
            "ancestor_list": ["[None]", "[42]", "[1]"],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_root_id(
        phylogeny_df,
        mutate=mutate,
    )
    assert (result_df["root_id"] == 42).all()

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_asexual2(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 42, 2, 3],
            "ancestor_id": [42, 42, 42, 1],
            "ancestor_list": ["[42]", "[None]", "[42]", "[1]"],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_root_id(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert (result_df["root_id"] == 42).all()

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_asexual3(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 0, 2, 3],
            "ancestor_list": ["[None]", "[None]", "[0]", "[1]"],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_root_id(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[1, "root_id"] == 1
    assert result_df.loc[0, "root_id"] == 0
    assert result_df.loc[2, "root_id"] == 0
    assert result_df.loc[3, "root_id"] == 1

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_sexual1(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[0, 1]"],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_root_id(
        phylogeny_df,
        mutate=mutate,
    )
    assert (result_df["root_id"] == 0).all()

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_sexual2(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 42, 2, 3],
            "ancestor_list": ["[None]", "[None]", "[1, 42]", "[2, 42]"],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_root_id(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[1, "root_id"] == 1
    assert result_df.loc[42, "root_id"] == 42
    assert result_df.loc[2, "root_id"] == 1
    assert result_df.loc[3, "root_id"] == 1

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_sexual3(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 0, 2, 3, 4],
            "ancestor_list": ["[None]", "[None]", "[0]", "[1]", "[1, 3]"],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_root_id(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[1, "root_id"] == 1
    assert result_df.loc[0, "root_id"] == 0
    assert result_df.loc[2, "root_id"] == 0
    assert result_df.loc[3, "root_id"] == 1
    assert result_df.loc[4, "root_id"] == 1

    if not mutate:
        assert original_df.equals(phylogeny_df)
