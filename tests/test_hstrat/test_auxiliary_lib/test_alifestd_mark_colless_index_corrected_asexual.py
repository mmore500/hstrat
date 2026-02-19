import os

import numpy as np
import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_find_leaf_ids,
    alifestd_find_root_ids,
    alifestd_has_multiple_roots,
    alifestd_is_strictly_bifurcating_asexual,
    alifestd_make_empty,
    alifestd_mark_colless_index_corrected_asexual,
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

    # Skip non-bifurcating phylogenies (they should raise ValueError)
    if not alifestd_is_strictly_bifurcating_asexual(phylogeny_df):
        with pytest.raises(ValueError, match="strictly bifurcating"):
            alifestd_mark_colless_index_corrected_asexual(phylogeny_df)
        return

    result = alifestd_mark_colless_index_corrected_asexual(phylogeny_df)

    assert alifestd_validate(result)
    assert original.equals(phylogeny_df)

    # Corrected Colless index should be non-negative
    assert all(result["colless_index_corrected"] >= 0)

    # Leaf nodes should have corrected Colless index 0
    leaf_ids = [*alifestd_find_leaf_ids(phylogeny_df)]
    for leaf_id in leaf_ids:
        val = result[result["id"] == leaf_id][
            "colless_index_corrected"
        ].squeeze()
        assert val == 0.0

    # Corrected index should be <= 1 for all nodes
    assert all(result["colless_index_corrected"] <= 1.0 + 1e-10)


def test_empty():
    res = alifestd_mark_colless_index_corrected_asexual(
        alifestd_make_empty(),
    )
    assert "colless_index_corrected" in res
    assert len(res) == 0


def test_non_bifurcating_raises():
    """Non-bifurcating trees should raise ValueError."""
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[1]"],
        }
    )
    with pytest.raises(ValueError, match="strictly bifurcating"):
        alifestd_mark_colless_index_corrected_asexual(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple_balanced(mutate: bool):
    r"""Test a balanced bifurcating tree.

          0
         / \
        1   2

    n=2 at root, so IC = 0.
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[0]"],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_colless_index_corrected_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    # n=2 at root -> IC = 0
    assert result_df.loc[0, "colless_index_corrected"] == 0.0
    assert result_df.loc[1, "colless_index_corrected"] == 0.0
    assert result_df.loc[2, "colless_index_corrected"] == 0.0

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple_imbalanced(mutate: bool):
    r"""Test an imbalanced bifurcating tree.

          0
         / \
        1   2
           / \
          3   4

    Node 0: n=3, C=1, IC = 2*1/((3-1)*(3-2)) = 2/2 = 1.0
    Node 2: n=2, IC = 0
    Leaves: IC = 0
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_list": ["[None]", "[0]", "[0]", "[2]", "[2]"],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_colless_index_corrected_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    assert result_df.loc[1, "colless_index_corrected"] == 0.0
    assert result_df.loc[3, "colless_index_corrected"] == 0.0
    assert result_df.loc[4, "colless_index_corrected"] == 0.0

    # Node 2: n=2, IC=0
    assert result_df.loc[2, "colless_index_corrected"] == 0.0

    # Node 0: n=3, C=1, IC = 2*1/(2*1) = 1.0
    assert result_df.loc[0, "colless_index_corrected"] == pytest.approx(
        1.0,
    )

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_caterpillar_tree(mutate: bool):
    r"""Test a caterpillar tree (maximally imbalanced).

          0
         / \
        1   2
           / \
          3   4
             / \
            5   6

    Node 4: n=2, IC=0
    Node 2: n=3, C=1, IC = 2*1/(2*1) = 1.0
    Node 0: n=4, C=3, IC = 2*3/(3*2) = 6/6 = 1.0
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_list": [
                "[None]",
                "[0]",
                "[0]",
                "[2]",
                "[2]",
                "[4]",
                "[4]",
            ],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_colless_index_corrected_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    # Leaves
    for leaf in [1, 3, 5, 6]:
        assert result_df.loc[leaf, "colless_index_corrected"] == 0.0

    # Node 4: n=2, IC=0
    assert result_df.loc[4, "colless_index_corrected"] == 0.0

    # Node 2: n=3, C=1, IC = 2/2 = 1.0
    assert result_df.loc[2, "colless_index_corrected"] == pytest.approx(
        1.0,
    )

    # Node 0: n=4, C=3, IC = 6/6 = 1.0
    assert result_df.loc[0, "colless_index_corrected"] == pytest.approx(
        1.0,
    )

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_larger_balanced_tree(mutate: bool):
    r"""Test a perfectly balanced tree with 4 leaves.

            0
           / \
          1   2
         / \ / \
        3  4 5  6

    Node 1: n=2, IC=0
    Node 2: n=2, IC=0
    Node 0: n=4, C=0 (balanced), IC = 0
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_list": [
                "[None]",
                "[0]",
                "[0]",
                "[1]",
                "[1]",
                "[2]",
                "[2]",
            ],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_colless_index_corrected_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    # All nodes should have IC=0 in a perfectly balanced tree
    for node_id in range(7):
        assert result_df.loc[node_id, "colless_index_corrected"] == 0.0

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_larger_imbalanced_tree(mutate: bool):
    r"""Test a larger imbalanced tree.

              0
             / \
            1   2
               / \
              3   4
                 / \
                5   6
                   / \
                  7   8

    n=5 at root, C=6
    IC = 2*6 / (4*3) = 12/12 = 1.0
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6, 7, 8],
            "ancestor_list": [
                "[None]",
                "[0]",
                "[0]",
                "[2]",
                "[2]",
                "[4]",
                "[4]",
                "[6]",
                "[6]",
            ],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_colless_index_corrected_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    # Root: n=5, C=6, IC = 2*6/(4*3) = 1.0
    assert result_df.loc[0, "colless_index_corrected"] == pytest.approx(
        1.0,
    )

    # Node 2: n=4, C=3, IC = 2*3/(3*2) = 1.0
    assert result_df.loc[2, "colless_index_corrected"] == pytest.approx(
        1.0,
    )

    # Node 4: n=3, C=1, IC = 2*1/(2*1) = 1.0
    assert result_df.loc[4, "colless_index_corrected"] == pytest.approx(
        1.0,
    )

    # Node 6: n=2, IC=0
    assert result_df.loc[6, "colless_index_corrected"] == 0.0

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_non_contiguous_ids(mutate: bool):
    """Test with non-contiguous IDs to exercise slow path."""
    phylogeny_df = pd.DataFrame(
        {
            "id": [10, 20, 30, 40, 50],
            "ancestor_list": ["[None]", "[10]", "[10]", "[30]", "[30]"],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_colless_index_corrected_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    # Root (10): n=3, C=1, IC = 2*1/(2*1) = 1.0
    assert result_df.loc[10, "colless_index_corrected"] == pytest.approx(
        1.0,
    )

    # Node 30: n=2, IC=0
    assert result_df.loc[30, "colless_index_corrected"] == 0.0

    # Leaves
    assert result_df.loc[20, "colless_index_corrected"] == 0.0
    assert result_df.loc[40, "colless_index_corrected"] == 0.0
    assert result_df.loc[50, "colless_index_corrected"] == 0.0

    if not mutate:
        assert original_df.equals(phylogeny_df)


def test_single_root():
    """Single node tree: n=1, IC=0."""
    phylogeny_df = pd.DataFrame(
        {
            "id": [0],
            "ancestor_list": ["[None]"],
        }
    )
    result_df = alifestd_mark_colless_index_corrected_asexual(
        phylogeny_df,
    )
    result_df.index = result_df["id"]
    assert result_df.loc[0, "colless_index_corrected"] == 0.0


def _make_comb_tree(n_leaves: int) -> pd.DataFrame:
    """Build a comb/caterpillar tree with `n_leaves` leaves.

    Structure (e.g. n_leaves=4):
          0
         / \
        1   2
           / \
          3   4
             / \
            5   6
    Internal nodes: 0, 2, 4, ...  Leaves: 1, 3, 5, 6
    """
    ids = []
    ancestors = []
    node_id = 0
    ids.append(node_id)
    ancestors.append("[None]")
    for i in range(n_leaves - 1):
        parent = node_id
        # left child (leaf)
        node_id += 1
        ids.append(node_id)
        ancestors.append(f"[{parent}]")
        if i < n_leaves - 2:
            # right child (internal, continues the chain)
            node_id += 1
            ids.append(node_id)
            ancestors.append(f"[{parent}]")
        else:
            # last split: right child is also a leaf
            node_id += 1
            ids.append(node_id)
            ancestors.append(f"[{parent}]")
    return pd.DataFrame({"id": ids, "ancestor_list": ancestors})


def _make_balanced_tree(depth: int) -> pd.DataFrame:
    """Build a perfectly balanced bifurcating tree of given depth.

    depth=1 -> 1 node (root only, n=1)
    depth=2 -> 3 nodes (root + 2 leaves, n=2)
    depth=3 -> 7 nodes (n=4 leaves)
    """
    ids = [0]
    ancestors = ["[None]"]
    next_id = 1
    queue = [0]
    for _ in range(depth - 1):
        next_queue = []
        for parent in queue:
            for _ in range(2):
                ids.append(next_id)
                ancestors.append(f"[{parent}]")
                next_queue.append(next_id)
                next_id += 1
        queue = next_queue
    return pd.DataFrame({"id": ids, "ancestor_list": ancestors})


@pytest.mark.parametrize("n_leaves", [3, 4, 5, 8, 10, 16, 32, 50])
def test_comb_tree_corrected_is_one(n_leaves: int):
    """Comb trees are maximally imbalanced; root IC should be 1.0."""
    phylogeny_df = _make_comb_tree(n_leaves)
    result_df = alifestd_mark_colless_index_corrected_asexual(
        phylogeny_df,
    )

    # All values should be in [0, 1]
    assert all(result_df["colless_index_corrected"] >= 0.0)
    assert all(result_df["colless_index_corrected"] <= 1.0 + 1e-10)

    # Root IC should be exactly 1.0 for a comb tree
    result_df.index = result_df["id"]
    assert result_df.loc[0, "colless_index_corrected"] == pytest.approx(
        1.0,
    )


@pytest.mark.parametrize("depth", [2, 3, 4, 5, 6, 7])
def test_balanced_tree_corrected_is_zero(depth: int):
    """Balanced trees are minimally imbalanced; root IC should be 0."""
    phylogeny_df = _make_balanced_tree(depth)
    result_df = alifestd_mark_colless_index_corrected_asexual(
        phylogeny_df,
    )

    # All values should be in [0, 1]
    assert all(result_df["colless_index_corrected"] >= 0.0)
    assert all(result_df["colless_index_corrected"] <= 1.0 + 1e-10)

    # Every node should have IC = 0 in a perfectly balanced tree
    assert all(result_df["colless_index_corrected"] == 0.0)


@pytest.mark.parametrize("n_leaves", [3, 4, 5, 8, 10, 16, 32, 50])
def test_comb_tree_all_subtrees_bounded(n_leaves: int):
    """Every subtree in a comb tree should have IC in [0, 1]."""
    phylogeny_df = _make_comb_tree(n_leaves)
    result_df = alifestd_mark_colless_index_corrected_asexual(
        phylogeny_df,
    )

    vals = result_df["colless_index_corrected"]
    assert all(vals >= -1e-10)
    assert all(vals <= 1.0 + 1e-10)

    # Internal nodes with n>2 leaves should have IC == 1.0
    # (every internal node in a comb is maximally imbalanced)
    result_df.index = result_df["id"]
    for _, row in result_df.iterrows():
        if "num_leaves" in result_df.columns and row["num_leaves"] > 2:
            assert row["colless_index_corrected"] == pytest.approx(
                1.0,
            )
