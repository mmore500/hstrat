import os
import typing

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_find_leaf_ids,
    alifestd_find_root_ids,
    alifestd_has_multiple_roots,
    alifestd_make_empty,
    alifestd_mark_num_leaves_sibling_asexual,
    alifestd_to_working_format,
    alifestd_validate,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
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

    result = alifestd_mark_num_leaves_sibling_asexual(phylogeny_df)

    assert alifestd_validate(result)
    assert original.equals(phylogeny_df)

    leaf_ids = [*alifestd_find_leaf_ids(phylogeny_df)]

    assert not alifestd_has_multiple_roots(phylogeny_df)
    (root_id,) = alifestd_find_root_ids(phylogeny_df)
    num_leaves = result[result["id"] == root_id][
        "num_leaves_sibling"
    ].squeeze()
    assert num_leaves == 0

    assert all(0 <= result["num_leaves_sibling"])
    assert all(result["num_leaves_sibling"] <= len(leaf_ids))


def test_empty():
    res = alifestd_mark_num_leaves_sibling_asexual(alifestd_make_empty())
    assert "num_leaves_sibling" in res
    assert len(res) == 0


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple1(apply: typing.Callable, mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[1]"],
        }
    )
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_num_leaves_sibling_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    assert result_df.loc[0, "num_leaves_sibling"] == 0
    assert result_df.loc[1, "num_leaves_sibling"] == 0
    assert result_df.loc[2, "num_leaves_sibling"] == 0

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple2(apply: typing.Callable, mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 0, 2, 3, 4],
            "ancestor_list": ["[0]", "[None]", "[0]", "[1]", "[1]"],
        }
    )
    phylogeny_df["id_"] = phylogeny_df["id"]
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_num_leaves_sibling_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id_"]
    assert result_df.loc[1, "num_leaves_sibling"] == 1
    assert result_df.loc[0, "num_leaves_sibling"] == 0
    assert result_df.loc[2, "num_leaves_sibling"] == 2
    assert result_df.loc[3, "num_leaves_sibling"] == 1
    assert result_df.loc[4, "num_leaves_sibling"] == 1

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple3(apply: typing.Callable, mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 0, 2, 3],
            "ancestor_list": ["[None]", "[None]", "[0]", "[1]"],
        }
    )
    phylogeny_df["id_"] = phylogeny_df["id"]
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_num_leaves_sibling_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id_"]
    assert result_df.loc[1, "num_leaves_sibling"] == 0
    assert result_df.loc[0, "num_leaves_sibling"] == 0
    assert result_df.loc[2, "num_leaves_sibling"] == 0
    assert result_df.loc[3, "num_leaves_sibling"] == 0

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple4(apply: typing.Callable, mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [1, 9, 2, 3, 7, 8],
            "ancestor_list": ["[9]", "[None]", "[9]", "[1]", "[9]", "[1]"],
        }
    )
    phylogeny_df["id_"] = phylogeny_df["id"]
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_num_leaves_sibling_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id_"]
    assert result_df.loc[1, "num_leaves_sibling"] == 2
    assert result_df.loc[9, "num_leaves_sibling"] == 0
    assert result_df.loc[2, "num_leaves_sibling"] == 3
    assert result_df.loc[3, "num_leaves_sibling"] == 1
    assert result_df.loc[7, "num_leaves_sibling"] == 3
    assert result_df.loc[8, "num_leaves_sibling"] == 1

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("apply", [lambda x: x, alifestd_to_working_format])
@pytest.mark.parametrize("mutate", [True, False])
def test_simple5(apply: typing.Callable, mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_list": ["[None]", "[0]", "[0]", "[1]", "[None]"],
        }
    )
    phylogeny_df["id_"] = phylogeny_df["id"]
    phylogeny_df = apply(phylogeny_df)
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_num_leaves_sibling_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id_"]
    assert result_df.loc[0, "num_leaves_sibling"] == 0
    assert result_df.loc[1, "num_leaves_sibling"] == 1
    assert result_df.loc[2, "num_leaves_sibling"] == 1
    assert result_df.loc[3, "num_leaves_sibling"] == 0
    assert result_df.loc[4, "num_leaves_sibling"] == 0

    if not mutate:
        assert original_df.equals(phylogeny_df)
