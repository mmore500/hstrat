import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_coarsen_taxa_asexual,
    alifestd_make_empty,
)


@pytest.mark.parametrize("col", ["id", "ancestor_id", "ancestor_list"])
def test_coarsen_agg_override_error(col: str):
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[1]"],
            "dummy": [1, 1, 1],
        }
    )
    with pytest.raises(ValueError):
        alifestd_coarsen_taxa_asexual(
            phylogeny_df,
            agg={col: "sum"},
            by="dummy",
        )


@pytest.mark.parametrize("mutate", [True, False])
def test_empty_coarsen(mutate: bool):
    phylogeny_df = alifestd_make_empty()
    # add the column we intend to group by
    phylogeny_df["dummy"] = pd.Series(dtype=int)
    result = alifestd_coarsen_taxa_asexual(
        phylogeny_df,
        mutate=mutate,
        by="dummy",
    )
    assert len(result) == 0


@pytest.mark.parametrize("mutate", [True, False])
def test_singleton_coarsen(mutate: bool):
    """
    A single‑node tree coarsens to itself.
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [42],
            "ancestor_list": ["[None]"],
            "branch_length": [0],
            "edge_length": [0],
            "origin_time": [100],
            "destruction_time": [200],
        }
    )
    phylogeny_df["group"] = 7
    original = phylogeny_df.copy()

    result = alifestd_coarsen_taxa_asexual(
        phylogeny_df,
        mutate=mutate,
        by="group",
    )

    # Should get exactly one row, same id, and each override respected:
    assert result.shape == (1, len(result.columns))
    row = result.iloc[0]
    assert row["id"] == 42
    assert row["branch_length"] == 0
    assert row["edge_length"] == 0
    assert row["origin_time"] == 100
    assert row["destruction_time"] == 200

    if not mutate:
        pd.testing.assert_frame_equal(phylogeny_df, original)


@pytest.mark.parametrize("mutate", [True, False])
def test_chain_coarsen(mutate: bool):
    # Chain 0 -> 1 -> 2, all rows share dummy=0, so you get
    #   - one taxon at the root (id=0),
    #   - one taxon for the chain below (id=2, since we take 'last' for id).
    # branch_length is summed, origin_time takes the first.
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[1]"],
            "branch_length": [0, 1, 2],
            "origin_time": [0, 10, 20],
        }
    )
    phylogeny_df["dummy"] = 0
    original = phylogeny_df.copy()

    result = alifestd_coarsen_taxa_asexual(
        phylogeny_df,
        mutate=mutate,
        by="dummy",
    )

    # should have exactly two clusters: one anchored at the root (0),
    # one for the rest of the chain (last id in that cluster is 2)
    ids = sorted(result["id"].tolist())
    assert ids == [2]

    # check sums and firsts
    bl = dict(zip(result["id"], result["branch_length"]))
    assert bl[2] == 0 + 1 + 2

    ot = dict(zip(result["id"], result["origin_time"]))
    assert ot[2] == 0

    if not mutate:
        # ensure input untouched
        pd.testing.assert_frame_equal(phylogeny_df, original)


@pytest.mark.parametrize("mutate", [True, False])
def test_star_coarsen(mutate: bool):
    # Star tree 0 -> {1,2}, all share dummy=0.
    # Depth=1 means each child winds up its own cluster,
    # so you get three rows back, with branch_length identical.
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[0]"],
            "branch_length": [0, 5, 5],
            "origin_time": [0, 50, 100],
        }
    )
    phylogeny_df["dummy"] = 0
    original = phylogeny_df.copy()

    result = alifestd_coarsen_taxa_asexual(
        phylogeny_df,
        mutate=mutate,
        by="dummy",
    )

    # root plus each leaf separately
    ids = sorted(result["id"].tolist())
    assert ids == [2]

    if not mutate:
        pd.testing.assert_frame_equal(phylogeny_df, original)


@pytest.mark.parametrize("mutate", [True, False])
def test_group_by_sequence(mutate: bool):
    # Supplying `by` as a sequence should behave same as single key.
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[1]"],
            "branch_length": [0, 1, 2],
            "origin_time": [0, 10, 20],
        }
    )
    phylogeny_df["g1"] = 0
    phylogeny_df["g2"] = 1
    original = phylogeny_df.copy()

    single = (
        alifestd_coarsen_taxa_asexual(phylogeny_df, mutate=mutate, by="g1")
        .sort_values("id")
        .reset_index(drop=True)
    )
    seq = (
        alifestd_coarsen_taxa_asexual(phylogeny_df, mutate=mutate, by=["g1"])
        .sort_values("id")
        .reset_index(drop=True)
    )

    pd.testing.assert_frame_equal(single, seq)

    if not mutate:
        pd.testing.assert_frame_equal(phylogeny_df, original)


@pytest.mark.parametrize("mutate", [True, False])
def test_chain_coarsen_with_overrides(mutate: bool):
    # Chain 0 -> 1 -> 2, all share group=0. Check that:
    #   - branch_length is summed
    #   - edge_length is summed
    #   - origin_time takes the first
    #   - destruction_time takes the last
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[1]"],
            "branch_length": [0, 1, 2],
            "edge_length": [0, 2, 3],
            "origin_time": [0, 10, 20],
            "destruction_time": [5, 6, 7],
        }
    )
    phylogeny_df["group"] = [0, 1, 1]
    original = phylogeny_df.copy()

    result = alifestd_coarsen_taxa_asexual(
        phylogeny_df,
        mutate=mutate,
        by="group",
    )
    ids = sorted(result["id"])
    assert ids == [0, 2]

    agg = {row["id"]: row for _, row in result.iterrows()}
    # root cluster
    assert agg[0]["branch_length"] == 0
    assert agg[0]["edge_length"] == 0
    assert agg[0]["origin_time"] == 0
    assert agg[0]["destruction_time"] == 5
    # lower cluster
    assert agg[2]["branch_length"] == 1 + 2
    assert agg[2]["edge_length"] == 2 + 3
    assert agg[2]["origin_time"] == 10
    assert agg[2]["destruction_time"] == 7

    if not mutate:
        pd.testing.assert_frame_equal(phylogeny_df, original)


@pytest.mark.parametrize("mutate", [True, False])
def test_multiple_independent_chains(mutate: bool):
    # Two disjoint chains with group=0 or group=1.
    # Each chain collapses into two clusters.
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5],
            "ancestor_list": [
                "[None]",
                "[0]",
                "[1]",
                "[None]",
                "[3]",
                "[4]",
            ],
            "branch_length": [0, 1, 2, 0, 3, 4],
            "origin_time": [0, 10, 20, 5, 15, 25],
        }
    )
    phylogeny_df["group"] = [0, 1, 1, 2, 3, 3]
    original = phylogeny_df.copy()

    result = alifestd_coarsen_taxa_asexual(
        phylogeny_df,
        mutate=mutate,
        by="group",
    )
    ids = sorted(result["id"])
    assert ids == [0, 2, 3, 5]

    agg = {row["id"]: row for _, row in result.iterrows()}
    assert agg[0]["branch_length"] == 0
    assert agg[2]["branch_length"] == 1 + 2
    assert agg[3]["branch_length"] == 0
    assert agg[5]["branch_length"] == 3 + 4

    if not mutate:
        pd.testing.assert_frame_equal(phylogeny_df, original)


@pytest.mark.parametrize("mutate", [True, False])
def test_chain_two_group_keys(mutate: bool):
    # Chain 0 -> 1 -> 2, grouped by TWO keys:
    #   - g1 is constant
    #   - g2 flips from 0 → 1 at node 1
    # So we should break into two clusters:
    #   - cluster at 0 alone
    #   - cluster of [1,2] together
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[1]"],
            "branch_length": [0, 1, 2],
            "origin_time": [0, 10, 20],
        }
    )
    # g1 same throughout, g2 flips at node 1 and stays
    phylogeny_df["g1"] = [0, 0, 0]
    phylogeny_df["g2"] = [0, 1, 1]
    phylogeny_df["g3"] = ["A", "A", "A"]
    original = phylogeny_df.copy()

    result = alifestd_coarsen_taxa_asexual(
        phylogeny_df,
        mutate=mutate,
        by=["g1", "g2"],
    )
    # Expect two clusters: ids 0 and 2
    assert sorted(result["id"]) == [0, 2]

    agg = {row["id"]: row for _, row in result.iterrows()}
    # root cluster
    assert agg[0]["branch_length"] == 0
    assert agg[0]["origin_time"] == 0
    # lower cluster
    assert agg[2]["branch_length"] == 1 + 2
    assert agg[2]["origin_time"] == 10

    if not mutate:
        pd.testing.assert_frame_equal(phylogeny_df, original)
