import os
import typing

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_find_root_ids,
    alifestd_make_empty,
    alifestd_mark_roots,
    alifestd_try_add_ancestor_id_col,
    alifestd_validate,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize(
    "apply", [alifestd_try_add_ancestor_id_col, lambda x: x]
)
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
def test_fuzz(apply: typing.Callable, phylogeny_df: pd.DataFrame):
    phylogeny_df = apply(phylogeny_df)
    original = phylogeny_df.copy()

    result = alifestd_mark_roots(phylogeny_df)

    assert alifestd_validate(result)
    assert original.equals(phylogeny_df)

    root_ids = [*alifestd_find_root_ids(phylogeny_df)]
    for root_id in root_ids:
        is_root = result[result["id"] == root_id]["is_root"].squeeze()
        assert is_root

    assert all(0 <= result["is_root"])
    assert all(result["is_root"] <= 1)


@pytest.mark.parametrize(
    "apply", [alifestd_try_add_ancestor_id_col, lambda x: x]
)
def test_empty(apply: typing.Callable):
    res = alifestd_mark_roots(apply(alifestd_make_empty()))
    assert "is_root" in res
    assert len(res) == 0


@pytest.mark.parametrize(
    "apply", [alifestd_try_add_ancestor_id_col, lambda x: x]
)
@pytest.mark.parametrize("mutate", [True, False])
def test_simple(apply: typing.Callable, mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[1]"],
        }
    )
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_roots(
        phylogeny_df,
        mutate=mutate,
    )
    assert result_df.loc[0, "is_root"]
    assert not result_df.loc[1, "is_root"]
    assert not result_df.loc[2, "is_root"]

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize(
    "apply", [alifestd_try_add_ancestor_id_col, lambda x: x]
)
@pytest.mark.parametrize("mutate", [True, False])
def test_simple2(apply: typing.Callable, mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 0, 2, 3],
            "ancestor_list": ["[0]", "[None]", "[0]", "[1]"],
        }
    )
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_roots(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert not result_df.loc[1, "is_root"]
    assert result_df.loc[0, "is_root"]
    assert not result_df.loc[2, "is_root"]
    assert not result_df.loc[3, "is_root"]

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize(
    "apply", [alifestd_try_add_ancestor_id_col, lambda x: x]
)
@pytest.mark.parametrize("mutate", [True, False])
def test_simple3(apply: typing.Callable, mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 0, 2, 3],
            "ancestor_list": ["[None]", "[None]", "[0]", "[0, 1]"],
        }
    )
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_roots(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[1, "is_root"]
    assert result_df.loc[0, "is_root"]
    assert not result_df.loc[2, "is_root"]
    assert not result_df.loc[3, "is_root"]

    if not mutate:
        assert original_df.equals(phylogeny_df)
