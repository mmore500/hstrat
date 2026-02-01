import os

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_find_leaf_ids,
    alifestd_find_root_ids,
    alifestd_has_multiple_roots,
    alifestd_make_empty,
    alifestd_mark_sackin_index_asexual,
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

    result = alifestd_mark_sackin_index_asexual(phylogeny_df)

    assert alifestd_validate(result)
    assert original.equals(phylogeny_df)

    # Sackin index should be non-negative
    assert all(result["sackin_index"] >= 0)

    # Leaf nodes should have Sackin index 0
    leaf_ids = [*alifestd_find_leaf_ids(phylogeny_df)]
    for leaf_id in leaf_ids:
        sackin = result[result["id"] == leaf_id]["sackin_index"].squeeze()
        assert sackin == 0

    # Root Sackin index should be non-negative
    # Note: For bifurcating version, root may not have max if it's not bifurcating
    if not alifestd_has_multiple_roots(phylogeny_df):
        (root_id,) = alifestd_find_root_ids(phylogeny_df)
        root_sackin = result[result["id"] == root_id]["sackin_index"].squeeze()
        assert root_sackin >= 0


def test_empty():
    res = alifestd_mark_sackin_index_asexual(alifestd_make_empty())
    assert "sackin_index" in res
    assert len(res) == 0


@pytest.mark.parametrize("mutate", [True, False])
def test_simple_chain(mutate: bool):
    """Test a simple chain/caterpillar tree: 0 -> 1 -> 2.

    All nodes are unifurcating, so Sackin index should be 0 everywhere
    (no bifurcating nodes to contribute).
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[1]"],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_sackin_index_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    # All unifurcating nodes -> Sackin = 0 everywhere
    assert result_df.loc[0, "sackin_index"] == 0
    assert result_df.loc[1, "sackin_index"] == 0
    assert result_df.loc[2, "sackin_index"] == 0

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple_bifurcating_balanced(mutate: bool):
    r"""Test a balanced bifurcating tree.

          0
         / \
        1   2

    Node 0 has 2 children, each with 1 leaf.
    Sackin at root = (0 + 1) + (0 + 1) = 2
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[0]"],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_sackin_index_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    # Leaves have Sackin = 0
    assert result_df.loc[1, "sackin_index"] == 0
    assert result_df.loc[2, "sackin_index"] == 0

    # Root: sum of (child_sackin + child_leaves) = (0+1) + (0+1) = 2
    assert result_df.loc[0, "sackin_index"] == 2

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple_bifurcating_imbalanced(mutate: bool):
    r"""Test an imbalanced bifurcating tree.

          0
         / \
        1   2
           / \
          3   4

    Leaves: 1, 3, 4 (depths from root: 1, 2, 2)
    Node 2: sackin = (0+1) + (0+1) = 2
    Node 0: sackin = (0+1) + (2+2) = 5

    Total Sackin at root = 1 + 2 + 2 = 5
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_list": ["[None]", "[0]", "[0]", "[2]", "[2]"],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_sackin_index_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    # Leaves have Sackin = 0
    assert result_df.loc[1, "sackin_index"] == 0
    assert result_df.loc[3, "sackin_index"] == 0
    assert result_df.loc[4, "sackin_index"] == 0

    # Node 2: (0+1) + (0+1) = 2
    assert result_df.loc[2, "sackin_index"] == 2

    # Node 0: (0+1) + (2+2) = 5
    assert result_df.loc[0, "sackin_index"] == 5

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_caterpillar_tree(mutate: bool):
    r"""Test a caterpillar/comb tree (maximally imbalanced).

          0
         / \
        1   2
           / \
          3   4
             / \
            5   6

    Leaves: 1 (depth 1), 3 (depth 2), 5 (depth 3), 6 (depth 3)
    Node 4: (0+1) + (0+1) = 2
    Node 2: (0+1) + (2+2) = 5
    Node 0: (0+1) + (5+3) = 9

    Total Sackin = 1 + 2 + 3 + 3 = 9
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
    result_df = alifestd_mark_sackin_index_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    # Leaves have Sackin = 0
    assert result_df.loc[1, "sackin_index"] == 0
    assert result_df.loc[3, "sackin_index"] == 0
    assert result_df.loc[5, "sackin_index"] == 0
    assert result_df.loc[6, "sackin_index"] == 0

    # Node 4: (0+1) + (0+1) = 2
    assert result_df.loc[4, "sackin_index"] == 2

    # Node 2: (0+1) + (2+2) = 5
    assert result_df.loc[2, "sackin_index"] == 5

    # Node 0: (0+1) + (5+3) = 9
    assert result_df.loc[0, "sackin_index"] == 9

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_polytomy_ignored(mutate: bool):
    r"""Test that polytomies (>2 children) do not contribute.

          0
        / | \
       1  2  3

    Node 0 has 3 children, so it doesn't contribute (not bifurcating).
    Sackin at root = 0.
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_list": ["[None]", "[0]", "[0]", "[0]"],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_sackin_index_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    # Leaves have Sackin = 0
    assert result_df.loc[1, "sackin_index"] == 0
    assert result_df.loc[2, "sackin_index"] == 0
    assert result_df.loc[3, "sackin_index"] == 0

    # Root with 3 children -> no contribution (polytomy ignored)
    assert result_df.loc[0, "sackin_index"] == 0

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_polytomy_with_bifurcating_subtree(mutate: bool):
    r"""Test tree with polytomy at root but bifurcating subtree.

            0
          / | \
         1  2  3
              / \
             4   5

    Node 3 is bifurcating: sackin = (0+1) + (0+1) = 2
    Node 0 has 3 children: no contribution (polytomy)
    Subtree values don't propagate through polytomy.
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5],
            "ancestor_list": ["[None]", "[0]", "[0]", "[0]", "[3]", "[3]"],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_sackin_index_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    # Leaves have Sackin = 0
    assert result_df.loc[1, "sackin_index"] == 0
    assert result_df.loc[2, "sackin_index"] == 0
    assert result_df.loc[4, "sackin_index"] == 0
    assert result_df.loc[5, "sackin_index"] == 0

    # Node 3: bifurcating -> (0+1) + (0+1) = 2
    assert result_df.loc[3, "sackin_index"] == 2

    # Node 0: 3 children -> polytomy, no contribution
    assert result_df.loc[0, "sackin_index"] == 0

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
    result_df = alifestd_mark_sackin_index_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    # Same structure as test_simple_bifurcating_imbalanced
    # Leaves have Sackin = 0
    assert result_df.loc[20, "sackin_index"] == 0
    assert result_df.loc[40, "sackin_index"] == 0
    assert result_df.loc[50, "sackin_index"] == 0

    # Node 30: (0+1) + (0+1) = 2
    assert result_df.loc[30, "sackin_index"] == 2

    # Node 10: (0+1) + (2+2) = 5
    assert result_df.loc[10, "sackin_index"] == 5

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_multiple_roots(mutate: bool):
    """Test with multiple roots (forest)."""
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_list": ["[None]", "[None]", "[0]", "[1]"],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_sackin_index_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    # Two separate trees, each with one child (unifurcating)
    # All nodes have Sackin = 0
    assert result_df.loc[0, "sackin_index"] == 0
    assert result_df.loc[1, "sackin_index"] == 0
    assert result_df.loc[2, "sackin_index"] == 0
    assert result_df.loc[3, "sackin_index"] == 0

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

    Leaves: 1 (depth 1), 3 (depth 2), 5 (depth 3), 7 (depth 4), 8 (depth 4)
    Node 6: (0+1) + (0+1) = 2
    Node 4: (0+1) + (2+2) = 5
    Node 2: (0+1) + (5+3) = 9
    Node 0: (0+1) + (9+4) = 14

    Total Sackin = 1 + 2 + 3 + 4 + 4 = 14
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
    result_df = alifestd_mark_sackin_index_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    # Leaves have Sackin = 0
    assert result_df.loc[1, "sackin_index"] == 0
    assert result_df.loc[3, "sackin_index"] == 0
    assert result_df.loc[5, "sackin_index"] == 0
    assert result_df.loc[7, "sackin_index"] == 0
    assert result_df.loc[8, "sackin_index"] == 0

    # Node 6: (0+1) + (0+1) = 2
    assert result_df.loc[6, "sackin_index"] == 2

    # Node 4: (0+1) + (2+2) = 5
    assert result_df.loc[4, "sackin_index"] == 5

    # Node 2: (0+1) + (5+3) = 9
    assert result_df.loc[2, "sackin_index"] == 9

    # Node 0: (0+1) + (9+4) = 14
    assert result_df.loc[0, "sackin_index"] == 14

    if not mutate:
        assert original_df.equals(phylogeny_df)
