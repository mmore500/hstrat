import os

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_find_leaf_ids,
    alifestd_find_root_ids,
    alifestd_make_empty,
    alifestd_mark_node_depth_asexual,
    alifestd_unfurl_traversal_postorder_asexual,
    is_nondecreasing,
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

    result = alifestd_unfurl_traversal_postorder_asexual(phylogeny_df)

    assert original.equals(phylogeny_df)

    assert len(result) == len(phylogeny_df)
    assert set(result) == set(phylogeny_df["id"])

    reference_df = alifestd_mark_node_depth_asexual(phylogeny_df)
    node_depths = dict(
        zip(
            reference_df["id"],
            reference_df["node_depth"],
        ),
    )
    node_depths = [node_depths[id_] for id_ in reversed(result)]
    assert is_nondecreasing(node_depths)

    assert result[-1] in alifestd_find_root_ids(phylogeny_df)
    assert result[0] in alifestd_find_leaf_ids(phylogeny_df)


def test_empty():
    res = alifestd_unfurl_traversal_postorder_asexual(alifestd_make_empty())
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
    result = alifestd_unfurl_traversal_postorder_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    assert result.tolist() == [2, 1, 0]

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
    result = alifestd_unfurl_traversal_postorder_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    assert result.tolist() == [3, 2, 0, 1]

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple3(mutate: bool):
    phylogeny_df = pd.DataFrame(
        {
            "id": [4, 0, 2, 3],
            "ancestor_list": ["[None]", "[None]", "[0]", "[4]"],
        },
    )
    original_df = phylogeny_df.copy()
    result = alifestd_unfurl_traversal_postorder_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    assert result.tolist() == [3, 2, 4, 0]

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
    result = alifestd_unfurl_traversal_postorder_asexual(
        phylogeny_df,
        mutate=mutate,
    )

    assert result.tolist() == [3, 2, 1, 0]

    if not mutate:
        assert original_df.equals(phylogeny_df)
