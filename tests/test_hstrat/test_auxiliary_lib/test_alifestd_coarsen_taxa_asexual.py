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
    # A single-node tree coarsens to itself.
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
    assert "branch_length" not in result
    assert "edge_length" not in result

    # Should get exactly one row, same id, and each override respected:
    assert result.shape == (1, len(result.columns))
    row = result.iloc[0]
    assert row["id"] == 42
    assert row["origin_time"] == 100
    assert row["destruction_time"] == 200

    if not mutate:
        pd.testing.assert_frame_equal(phylogeny_df, original)


@pytest.mark.parametrize("mutate", [True, False])
def test_chain_coarsen(mutate: bool):
    # Chain 0 -> 1 -> 2, all rows share dummy=0, so you get
    #   - one taxon at the root (id=0),
    #   - one taxon for the chain below (id=1, since we take 'first' for id).
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

    assert result["id"].tolist() == [0]
    assert result["ancestor_id"].tolist() == [0]
    assert "branch_length" not in result
    assert "edge_length" not in result

    if not mutate:
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

    assert result["id"].tolist() == [0]
    assert result["ancestor_id"].tolist() == [0]

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
    assert ids == [0, 1]
    assert "branch_length" not in result
    assert "edge_length" not in result

    agg = {row["id"]: row for _, row in result.iterrows()}
    # root cluster
    assert agg[0]["origin_time"] == 0
    assert agg[0]["destruction_time"] == 5
    assert agg[0]["ancestor_id"] == 0
    # lower cluster
    assert agg[1]["origin_time"] == 10
    assert agg[1]["destruction_time"] == 7
    assert agg[1]["ancestor_id"] == 0

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
    assert ids == [0, 1, 3, 4]

    assert "branch_length" not in result

    if not mutate:
        pd.testing.assert_frame_equal(phylogeny_df, original)


@pytest.mark.parametrize("mutate", [True, False])
def test_chain_two_group_keys(mutate: bool):
    # Chain 0 -> 1 -> 2, grouped by TWO keys:
    #   - g1 is constant
    #   - g2 flips from 0 -> 1 at node 1
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
    # Expect two clusters: ids 0 and 1
    assert sorted(result["id"]) == [0, 1]
    assert "branch_length" not in result

    agg = {row["id"]: row for _, row in result.iterrows()}
    # root cluster
    assert agg[0]["ancestor_id"] == 0
    assert agg[0]["origin_time"] == 0
    # lower cluster
    assert agg[1]["ancestor_id"] == 0
    assert agg[1]["origin_time"] == 10

    if not mutate:
        pd.testing.assert_frame_equal(phylogeny_df, original)


@pytest.mark.parametrize("mutate", [True, False])
def test_branching_disconnected_same_group_with_parent_id(mutate: bool):
    # 10-node tree with single-parent pointers:
    #
    #       0
    #      / \
    #     1   2
    #    / \ / \
    #   3  4 5  6
    #  /      \  \
    # 7        8  9
    #
    # ancestor_id maps each node to exactly one parent (or None for root).
    # Groups:
    #   - 'root' on {0,1,2}
    #   - 'A' on two disconnected clades {3 -> 7} and {5 -> 8}
    #   - 'B' on two others {4} and {6 -> 9}
    #
    # Expect six clusters: one per contiguous segment per leaf path:
    #   - root-clade under 1        -> id=1
    #   - root-clade under 2        -> id=2
    #   - A-clade under 3 -> 7      -> id=7
    #   - A-clade under 5 ->        -> id=8
    #   - B-clade leaf 4            -> id=4
    #   - B-clade under 6 -> 9      -> id=9
    N = 10
    df = pd.DataFrame(
        {
            "id": list(range(N)),
            "ancestor_id": [0, 0, 0, 1, 1, 2, 2, 3, 5, 6],
            "branch_length": [1] * N,
            "edge_length": [2] * N,
            "origin_time": list(range(N)),
            "destruction_time": [i + 10 for i in range(N)],
        }
    )
    df["grp"] = [
        "root",  # 0
        "root",  # 1
        "root",  # 2
        "A",  # 3
        "root",  # 4
        "A",  # 5
        "B",  # 6
        "A",  # 7
        "A",  # 8
        "A",  # 9
    ]
    original = df.copy()

    result = alifestd_coarsen_taxa_asexual(
        df,
        mutate=mutate,
        by="grp",
    )

    # Expect exactly these terminal ids
    expected_ids = [0, 3, 5, 6, 9]
    assert sorted(result["id"].tolist()) == expected_ids

    # Check ancestor_ids
    anc = dict(zip(result["id"], result["ancestor_id"]))
    assert anc[0] == 0
    assert anc[3] == 0
    assert anc[5] == 0
    assert anc[6] == 0
    assert anc[9] == 6

    # Check origin_time = first in cluster, destruction_time = last
    ot = dict(zip(result["id"], result["origin_time"]))
    dt = dict(zip(result["id"], result["destruction_time"]))
    assert ot[0] == 0 and dt[0] == 14
    assert ot[3] == 3 and dt[3] == 17
    assert ot[5] == 5 and dt[5] == 18
    assert ot[6] == 6 and dt[6] == 16
    assert ot[9] == 9 and dt[9] == 19

    if not mutate:
        pd.testing.assert_frame_equal(df, original)


@pytest.mark.parametrize("mutate", [True, False])
def test_branching_disconnected_same_group_with_parent_id2(mutate: bool):
    # 10-node tree with single-parent pointers:
    #
    #       0
    #      / \
    #     1   2
    #    / \ / \
    #   3  4 5  6
    #  /      \  \
    # 7        8  99
    N = 10
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6, 7, 8, 99],
            "ancestor_id": [0, 0, 0, 1, 1, 2, 2, 3, 5, 6],
            "branch_length": [1] * N,
            "edge_length": [2] * N,
            "origin_time": list(range(N)),
            "destruction_time": [i + 10 for i in range(N)],
        }
    )
    df["grp"] = [
        "root",  # 0
        "root",  # 1
        "root",  # 2
        "A",  # 3
        "root",  # 4
        "A",  # 5
        "B",  # 6
        "A",  # 7
        "A",  # 8
        "A",  # 99
    ]
    df = df[::-1].copy()  # reverse (not topologically sorted)
    original = df.copy()

    result = alifestd_coarsen_taxa_asexual(
        df,
        mutate=mutate,
        by="grp",
    )

    # Expect exactly these terminal ids
    expected_ids = [0, 3, 5, 6, 99]
    assert sorted(result["id"].tolist()) == expected_ids

    # Check ancestor_ids
    anc = dict(zip(result["id"], result["ancestor_id"]))
    assert anc[0] == 0
    assert anc[3] == 0
    assert anc[5] == 0
    assert anc[6] == 0
    assert anc[99] == 6

    # Check origin_time = first in cluster, destruction_time = last
    ot = dict(zip(result["id"], result["origin_time"]))
    dt = dict(zip(result["id"], result["destruction_time"]))
    assert ot[0] == 0 and dt[0] == 14
    assert ot[3] == 3 and dt[3] == 17
    assert ot[5] == 5 and dt[5] == 18
    assert ot[6] == 6 and dt[6] == 16
    assert ot[99] == 9 and dt[99] == 19

    if not mutate:
        pd.testing.assert_frame_equal(df, original)
