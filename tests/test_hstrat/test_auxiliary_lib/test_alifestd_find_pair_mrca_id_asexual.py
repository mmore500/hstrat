import os

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_find_mrca_id_asexual,
    alifestd_to_working_format,
)
from hstrat._auxiliary_lib._alifestd_find_pair_mrca_id_asexual import (
    alifestd_find_pair_mrca_id_asexual,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


@pytest.mark.parametrize(
    "phylogeny_df",
    [
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_ecoeaselection.csv")
        ),
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_lexicaseselection.csv")
        ),
        alifestd_to_working_format(
            pd.read_csv(f"{assets_path}/nk_tournamentselection.csv")
        ),
    ],
)
def test_fuzz_matches_existing(phylogeny_df: pd.DataFrame):
    """Verify pair mrca matches the multi-id mrca function on real data."""
    ids = phylogeny_df["id"].tolist()
    for i in ids[:5]:
        for j in ids[:5]:
            expected = alifestd_find_mrca_id_asexual(
                phylogeny_df, [i, j], mutate=False
            )
            actual = alifestd_find_pair_mrca_id_asexual(
                phylogeny_df, i, j, mutate=False
            )
            assert actual == expected


@pytest.mark.parametrize("mutate", [True, False])
def test_simple1(mutate: bool):
    # Tree:  0 -> 1 -> 2, 0 -> 3
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [0, 0, 1, 0],
        }
    )
    original_df = phylogeny_df.copy()

    assert (
        alifestd_find_pair_mrca_id_asexual(phylogeny_df, 0, 1, mutate=mutate)
        == 0
    )
    assert (
        alifestd_find_pair_mrca_id_asexual(phylogeny_df, 1, 2, mutate=mutate)
        == 1
    )
    assert (
        alifestd_find_pair_mrca_id_asexual(phylogeny_df, 2, 3, mutate=mutate)
        == 0
    )
    assert (
        alifestd_find_pair_mrca_id_asexual(phylogeny_df, 2, 2, mutate=mutate)
        == 2
    )
    assert (
        alifestd_find_pair_mrca_id_asexual(phylogeny_df, 0, 0, mutate=mutate)
        == 0
    )

    if not mutate:
        assert original_df.equals(phylogeny_df)


def test_simple_with_ancestor_list():
    phylogeny_df = alifestd_to_working_format(
        pd.DataFrame(
            {
                "id": [0, 1, 2, 3],
                "ancestor_list": ["[None]", "[0]", "[1]", "[0]"],
            }
        )
    )
    assert alifestd_find_pair_mrca_id_asexual(phylogeny_df, 2, 3) == 0
    assert alifestd_find_pair_mrca_id_asexual(phylogeny_df, 1, 2) == 1


def test_single_node():
    phylogeny_df = pd.DataFrame(
        {
            "id": [0],
            "ancestor_id": [0],
        }
    )
    assert alifestd_find_pair_mrca_id_asexual(phylogeny_df, 0, 0) == 0


def test_multiple_roots_disjoint():
    """Two disjoint roots should return None."""
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_id": [0, 1, 2],
        }
    )
    assert alifestd_find_pair_mrca_id_asexual(phylogeny_df, 0, 1) is None
    assert alifestd_find_pair_mrca_id_asexual(phylogeny_df, 1, 2) is None
    assert alifestd_find_pair_mrca_id_asexual(phylogeny_df, 0, 0) == 0


def test_multiple_roots_partial():
    """Forest: tree1 = {0, 1}, tree2 = {2, 3}."""
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [0, 0, 2, 2],
        }
    )
    assert alifestd_find_pair_mrca_id_asexual(phylogeny_df, 0, 1) == 0
    assert alifestd_find_pair_mrca_id_asexual(phylogeny_df, 2, 3) == 2
    assert alifestd_find_pair_mrca_id_asexual(phylogeny_df, 0, 2) is None
    assert alifestd_find_pair_mrca_id_asexual(phylogeny_df, 1, 3) is None


def test_chain():
    """Straight chain: 0 -> 1 -> 2 -> 3."""
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [0, 0, 1, 2],
        }
    )
    assert alifestd_find_pair_mrca_id_asexual(phylogeny_df, 0, 3) == 0
    assert alifestd_find_pair_mrca_id_asexual(phylogeny_df, 1, 3) == 1
    assert alifestd_find_pair_mrca_id_asexual(phylogeny_df, 2, 3) == 2


def test_bypass_kwargs():
    """Test that is_topologically_sorted and has_contiguous_ids kwargs work."""
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [0, 0, 1, 0],
        }
    )
    result = alifestd_find_pair_mrca_id_asexual(
        phylogeny_df,
        2,
        3,
        is_topologically_sorted=True,
        has_contiguous_ids=True,
    )
    assert result == 0


def test_not_topologically_sorted_raises():
    """Should raise NotImplementedError for unsorted input."""
    phylogeny_df = pd.DataFrame(
        {
            "id": [3, 2, 1, 0],
            "ancestor_id": [2, 0, 0, 0],
        }
    )
    with pytest.raises(NotImplementedError):
        alifestd_find_pair_mrca_id_asexual(phylogeny_df, 0, 3)


def test_non_contiguous_ids_raises():
    """Should raise NotImplementedError for non-contiguous ids."""
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 2, 4],
            "ancestor_id": [0, 0, 2],
        }
    )
    with pytest.raises(NotImplementedError):
        alifestd_find_pair_mrca_id_asexual(phylogeny_df, 0, 4)
