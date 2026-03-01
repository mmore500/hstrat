import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_coarsen_dilate_asexual,
    alifestd_make_empty,
)


def test_empty():
    phylogeny_df = alifestd_make_empty()
    phylogeny_df["origin_time"] = pd.Series(dtype=float)
    result = alifestd_coarsen_dilate_asexual(
        phylogeny_df,
        dilation=2,
        ignore_topological_sensitivity=True,
    )
    assert len(result) == 0


@pytest.mark.parametrize("mutate", [True, False])
def test_singleton(mutate):
    df = pd.DataFrame(
        {
            "id": [0],
            "ancestor_id": [0],
            "origin_time": [5],
        }
    )
    original = df.copy()
    result = alifestd_coarsen_dilate_asexual(
        df,
        dilation=2,
        mutate=mutate,
        ignore_topological_sensitivity=True,
    )
    assert len(result) == 1
    assert result.iloc[0]["id"] == 0
    # Single node is a leaf, so origin_time should not change
    assert result.iloc[0]["origin_time"] == 5
    if not mutate:
        pd.testing.assert_frame_equal(df, original)


@pytest.mark.parametrize("mutate", [True, False])
def test_chain_dilation2(mutate):
    # Chain: 0 -> 1 -> 2 -> 3 -> 4 (leaf)
    # origin_time: 0, 1, 2, 3, 4
    # dilation=2: boundaries at 0, 2, 4
    # Inner nodes 0,1 snap to 0; 2,3 snap to 2; leaf 4 stays.
    # Merges: 0+1 -> 0, 2+3 -> 2, leaf 4 stays.
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_id": [0, 0, 1, 2, 3],
            "origin_time": [0, 1, 2, 3, 4],
        }
    )
    original = df.copy()
    result = alifestd_coarsen_dilate_asexual(
        df,
        dilation=2,
        mutate=mutate,
        ignore_topological_sensitivity=True,
    )
    assert sorted(result["id"].tolist()) == [0, 2, 4]
    ot = dict(zip(result["id"], result["origin_time"]))
    assert ot[0] == 0
    assert ot[2] == 2
    assert ot[4] == 4  # leaf unchanged
    anc = dict(zip(result["id"], result["ancestor_id"]))
    assert anc[0] == 0  # root
    assert anc[2] == 0
    assert anc[4] == 2
    if not mutate:
        pd.testing.assert_frame_equal(df, original)


@pytest.mark.parametrize("mutate", [True, False])
def test_chain_dilation1(mutate):
    # dilation=1: every integer is a boundary, so no merging.
    # Inner nodes snap to themselves (already on boundary).
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_id": [0, 0, 1, 2, 3],
            "origin_time": [0, 1, 2, 3, 4],
        }
    )
    result = alifestd_coarsen_dilate_asexual(
        df,
        dilation=1,
        mutate=mutate,
        ignore_topological_sensitivity=True,
    )
    assert len(result) == 5


@pytest.mark.parametrize("mutate", [True, False])
def test_chain_dilation_large(mutate):
    # dilation larger than all values: everything snaps to 0.
    # Inner nodes all merge into root, leaf stays.
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_id": [0, 0, 1, 2, 3],
            "origin_time": [0, 1, 2, 3, 4],
        }
    )
    result = alifestd_coarsen_dilate_asexual(
        df,
        dilation=100,
        mutate=mutate,
        ignore_topological_sensitivity=True,
    )
    assert sorted(result["id"].tolist()) == [0, 4]
    anc = dict(zip(result["id"], result["ancestor_id"]))
    assert anc[4] == 0


@pytest.mark.parametrize("mutate", [True, False])
def test_branching_tree(mutate):
    #       0 (t=0)
    #      / \
    #    1(t=1) 2(t=1)
    #    |       |
    #   3(t=2)  4(t=3)
    #    |       |
    #   5(t=4)  6(t=5)  <- leaves
    # dilation=2: boundaries at 0, 2, 4
    # 0->0, 1->0, 2->0 (merge with 0)
    # 3->2, 4->2 (separate branches, not merged with each other)
    # leaves 5(t=4), 6(t=5) stay
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_id": [0, 0, 0, 1, 2, 3, 4],
            "origin_time": [0, 1, 1, 2, 3, 4, 5],
        }
    )
    original = df.copy()
    result = alifestd_coarsen_dilate_asexual(
        df,
        dilation=2,
        mutate=mutate,
        ignore_topological_sensitivity=True,
    )
    assert sorted(result["id"].tolist()) == [0, 3, 4, 5, 6]
    anc = dict(zip(result["id"], result["ancestor_id"]))
    assert anc[0] == 0
    assert anc[3] == 0
    assert anc[4] == 0
    assert anc[5] == 3
    assert anc[6] == 4
    # Leaves unchanged
    ot = dict(zip(result["id"], result["origin_time"]))
    assert ot[5] == 4
    assert ot[6] == 5
    if not mutate:
        pd.testing.assert_frame_equal(df, original)


@pytest.mark.parametrize("mutate", [True, False])
def test_star_tree(mutate):
    # Root with all leaves: no inner nodes to collapse.
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [0, 0, 0, 0],
            "origin_time": [0, 1, 2, 3],
        }
    )
    result = alifestd_coarsen_dilate_asexual(
        df,
        dilation=2,
        mutate=mutate,
        ignore_topological_sensitivity=True,
    )
    # Root is the only inner node (but also a leaf if only child is leaf)
    # Actually root has children, so it's not a leaf
    # All others are leaves
    assert 0 in result["id"].tolist()
    # All leaf origin_times preserved
    for _, row in result.iterrows():
        if row["id"] != 0:
            orig_row = df.loc[df["id"] == row["id"]].iloc[0]
            assert row["origin_time"] == orig_row["origin_time"]


@pytest.mark.parametrize("mutate", [True, False])
def test_float_criterion(mutate):
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_id": [0, 0, 1, 2, 3],
            "origin_time": [0.0, 1.5, 3.0, 4.5, 6.0],
        }
    )
    result = alifestd_coarsen_dilate_asexual(
        df,
        dilation=3,
        mutate=mutate,
        ignore_topological_sensitivity=True,
    )
    # Inner: 0->0.0, 1->0.0, 2->3.0, 3->3.0
    # Merges: 0+1 -> 0, 2+3 -> 2
    # leaf 4 stays at 6.0
    assert sorted(result["id"].tolist()) == [0, 2, 4]
    ot = dict(zip(result["id"], result["origin_time"]))
    assert ot[0] == 0.0
    assert ot[2] == 3.0
    assert ot[4] == 6.0


@pytest.mark.parametrize("mutate", [True, False])
def test_integer_criterion(mutate):
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_id": [0, 0, 1, 2, 3],
            "origin_time": [0, 2, 4, 6, 8],
        }
    )
    result = alifestd_coarsen_dilate_asexual(
        df,
        dilation=4,
        mutate=mutate,
        ignore_topological_sensitivity=True,
    )
    # Inner snap: 0->0, 1->0, 2->4, 3->4
    # Merges: 0+1 -> 0, 2+3 -> 2
    # Leaf 4 at 8 stays
    assert sorted(result["id"].tolist()) == [0, 2, 4]
    ot = dict(zip(result["id"], result["origin_time"]))
    assert ot[0] == 0
    assert ot[2] == 4
    assert ot[4] == 8


def test_invalid_dilation():
    df = pd.DataFrame(
        {
            "id": [0],
            "ancestor_id": [0],
            "origin_time": [0],
        }
    )
    with pytest.raises(ValueError, match="dilation must be positive"):
        alifestd_coarsen_dilate_asexual(
            df,
            dilation=0,
            ignore_topological_sensitivity=True,
        )
    with pytest.raises(ValueError, match="dilation must be positive"):
        alifestd_coarsen_dilate_asexual(
            df,
            dilation=-1,
            ignore_topological_sensitivity=True,
        )


def test_missing_criterion():
    df = pd.DataFrame(
        {
            "id": [0],
            "ancestor_id": [0],
        }
    )
    with pytest.raises(ValueError, match="criterion column"):
        alifestd_coarsen_dilate_asexual(
            df,
            dilation=2,
            ignore_topological_sensitivity=True,
        )


def test_criterion_id_rejected():
    df = pd.DataFrame(
        {
            "id": [0],
            "ancestor_id": [0],
            "origin_time": [0],
        }
    )
    with pytest.raises(ValueError, match="must not be"):
        alifestd_coarsen_dilate_asexual(
            df,
            dilation=2,
            criterion="id",
            ignore_topological_sensitivity=True,
        )


def test_criterion_ancestor_id_rejected():
    df = pd.DataFrame(
        {
            "id": [0],
            "ancestor_id": [0],
            "origin_time": [0],
        }
    )
    with pytest.raises(ValueError, match="must not be"):
        alifestd_coarsen_dilate_asexual(
            df,
            dilation=2,
            criterion="ancestor_id",
            ignore_topological_sensitivity=True,
        )


def test_custom_criterion():
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_id": [0, 0, 1, 2, 3],
            "origin_time": [10, 20, 30, 40, 50],
            "my_time": [0, 1, 2, 3, 4],
        }
    )
    result = alifestd_coarsen_dilate_asexual(
        df,
        dilation=2,
        criterion="my_time",
        ignore_topological_sensitivity=True,
    )
    # Uses my_time for snapping, origin_time untouched
    assert sorted(result["id"].tolist()) == [0, 2, 4]
    ot = dict(zip(result["id"], result["origin_time"]))
    assert ot[0] == 10  # origin_time unchanged for kept rows
    assert ot[4] == 50


@pytest.mark.parametrize("mutate", [True, False])
def test_with_ancestor_list(mutate):
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_list": ["[none]", "[0]", "[1]", "[2]", "[3]"],
            "origin_time": [0, 1, 2, 3, 4],
        }
    )
    result = alifestd_coarsen_dilate_asexual(
        df,
        dilation=2,
        mutate=mutate,
        ignore_topological_sensitivity=True,
    )
    assert "ancestor_list" in result.columns
    assert "ancestor_id" in result.columns
    assert len(result) == 3


@pytest.mark.parametrize("mutate", [True, False])
def test_mrca_only_shifts_backward(mutate):
    # Verify MRCA shifts backward by at most dilation.
    #       0 (t=0)
    #      / \
    #    1(t=3) 2(t=3)  <- inner
    #    |       |
    #   3(t=7)  4(t=8)  <- leaves
    # dilation=5: boundaries at 0, 5
    # Inner: 0->0, 1->0, 2->0 (merge into 0)
    # leaves stay
    # Original MRCA of 3,4 is node 0 at t=0. After: still 0 at t=0.
    # Shift = 0. OK.
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_id": [0, 0, 0, 1, 2],
            "origin_time": [0, 3, 3, 7, 8],
        }
    )
    result = alifestd_coarsen_dilate_asexual(
        df,
        dilation=5,
        mutate=mutate,
        ignore_topological_sensitivity=True,
    )
    # leaves 3 and 4 must be in result
    assert 3 in result["id"].tolist()
    assert 4 in result["id"].tolist()
    # both should point to root (node 0)
    anc = dict(zip(result["id"], result["ancestor_id"]))
    assert anc[3] == 0
    assert anc[4] == 0


@pytest.mark.parametrize("mutate", [True, False])
def test_mrca_shift_bounded_by_dilation(mutate):
    # A case where MRCA shifts backward but within dilation.
    #       0 (t=0)
    #       |
    #      1 (t=1)
    #      / \
    #    2(t=2) 3(t=3)  <- leaves
    # dilation=2: boundaries at 0, 2
    # Inner: 0->0, 1->0 (merge into 0)
    # Original MRCA(2,3) = 1 at t=1.
    # After: MRCA(2,3) = 0 at t=0. Shift = 1 <= dilation=2.
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [0, 0, 1, 1],
            "origin_time": [0, 1, 2, 3],
        }
    )
    result = alifestd_coarsen_dilate_asexual(
        df,
        dilation=2,
        mutate=mutate,
        ignore_topological_sensitivity=True,
    )
    anc = dict(zip(result["id"], result["ancestor_id"]))
    assert anc[2] == 0  # MRCA shifted from 1 to 0
    assert anc[3] == 0
    ot = dict(zip(result["id"], result["origin_time"]))
    # Original MRCA was at t=1, new MRCA at t=0, shift = 1 <= 2
    assert ot[0] == 0


@pytest.mark.parametrize("mutate", [True, False])
def test_no_topological_change_still_snaps(mutate):
    # Even when no merging occurs, inner nodes should snap to boundary.
    #     0 (t=0)
    #     |
    #     1 (t=5)
    #     |
    #     2 (t=10) <- leaf
    # dilation=3: boundaries at 0, 3, 6, 9
    # Inner: 0->0, 1->3
    # No merging (different boundaries).
    # But 1 snaps from 5 to 3.
    df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_id": [0, 0, 1],
            "origin_time": [0, 5, 10],
        }
    )
    result = alifestd_coarsen_dilate_asexual(
        df,
        dilation=3,
        mutate=mutate,
        ignore_topological_sensitivity=True,
    )
    assert len(result) == 3
    ot = dict(zip(result["id"], result["origin_time"]))
    assert ot[0] == 0
    assert ot[1] == 3  # snapped from 5 to 3
    assert ot[2] == 10  # leaf unchanged


@pytest.mark.parametrize("mutate", [True, False])
def test_two_roots(mutate):
    # Two independent trees
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [0, 0, 2, 2],
            "origin_time": [0, 1, 0, 1],
        }
    )
    result = alifestd_coarsen_dilate_asexual(
        df,
        dilation=2,
        mutate=mutate,
        ignore_topological_sensitivity=True,
    )
    # Both trees: root + leaf. Leaves stay.
    assert 1 in result["id"].tolist()
    assert 3 in result["id"].tolist()


def test_inner_node_count_never_increases():
    # After coarsening, number of inner nodes should not increase.
    df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_id": [0, 0, 0, 1, 2, 3, 4],
            "origin_time": [0, 1, 1, 2, 3, 4, 5],
        }
    )
    original_inner = set()
    for _, row in df.iterrows():
        if row["id"] != row["ancestor_id"]:
            original_inner.add(int(row["ancestor_id"]))
    original_inner_count = len(original_inner)

    result = alifestd_coarsen_dilate_asexual(
        df,
        dilation=2,
        ignore_topological_sensitivity=True,
    )
    result_inner = set()
    for _, row in result.iterrows():
        if row["id"] != row["ancestor_id"]:
            result_inner.add(int(row["ancestor_id"]))
    result_inner_count = len(result_inner)

    assert result_inner_count <= original_inner_count
