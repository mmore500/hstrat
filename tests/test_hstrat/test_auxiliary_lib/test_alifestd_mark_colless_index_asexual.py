import os

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_find_leaf_ids,
    alifestd_find_root_ids,
    alifestd_has_multiple_roots,
    alifestd_make_empty,
    alifestd_mark_colless_index_asexual,
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

    result = alifestd_mark_colless_index_asexual(phylogeny_df)

    assert alifestd_validate(result)
    assert original.equals(phylogeny_df)

    # Colless index should be non-negative
    assert all(result["colless_index"] >= 0)

    # Leaf nodes should have Colless index 0
    leaf_ids = [*alifestd_find_leaf_ids(phylogeny_df)]
    for leaf_id in leaf_ids:
        colless = result[result["id"] == leaf_id]["colless_index"].squeeze()
        assert colless == 0

    # Root should have the highest or equal Colless index
    if not alifestd_has_multiple_roots(phylogeny_df):
        (root_id,) = alifestd_find_root_ids(phylogeny_df)
        root_colless = result[result["id"] == root_id][
            "colless_index"
        ].squeeze()
        assert root_colless >= 0
        # Root colless should be >= all other nodes' colless
        assert root_colless == result["colless_index"].max()


def test_empty():
    res = alifestd_mark_colless_index_asexual(alifestd_make_empty())
    assert "colless_index" in res
    assert len(res) == 0


@pytest.mark.parametrize("mutate", [True, False])
def test_simple_chain(mutate: bool):
    """Test a simple chain/caterpillar tree: 0 -> 1 -> 2.

    All nodes are unifurcating, so Colless index should be 0 everywhere.
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[1]"],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_colless_index_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    # All unifurcating nodes -> Colless = 0 everywhere
    assert result_df.loc[0, "colless_index"] == 0
    assert result_df.loc[1, "colless_index"] == 0
    assert result_df.loc[2, "colless_index"] == 0

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple_bifurcating_balanced(mutate: bool):
    r"""Test a balanced bifurcating tree.

          0
         / \
        1   2

    Each leaf has 1 leaf, so |1-1| = 0 at root.
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[0]"],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_colless_index_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    # Balanced tree -> Colless = 0
    assert result_df.loc[0, "colless_index"] == 0
    assert result_df.loc[1, "colless_index"] == 0
    assert result_df.loc[2, "colless_index"] == 0

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

    Node 0: children are 1 (1 leaf) and 2 (2 leaves), |1-2| = 1
    Node 2: children are 3 (1 leaf) and 4 (1 leaf), |1-1| = 0
    Total Colless at root = 1 + 0 = 1
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_list": ["[None]", "[0]", "[0]", "[2]", "[2]"],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_colless_index_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    # Leaves have Colless = 0
    assert result_df.loc[1, "colless_index"] == 0
    assert result_df.loc[3, "colless_index"] == 0
    assert result_df.loc[4, "colless_index"] == 0

    # Node 2 has two balanced children -> local = 0
    assert result_df.loc[2, "colless_index"] == 0

    # Node 0 has children with 1 and 2 leaves -> |1-2| = 1
    # Plus subtree Colless from children (0 + 0) = 1
    assert result_df.loc[0, "colless_index"] == 1

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

    Node 4: |1-1| = 0
    Node 2: children are 3 (1 leaf) and 4 (2 leaves), |1-2| = 1
    Node 0: children are 1 (1 leaf) and 2 (3 leaves), |1-3| = 2
    Total Colless at root = 2 + 1 + 0 = 3
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
    result_df = alifestd_mark_colless_index_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    # Leaves have Colless = 0
    assert result_df.loc[1, "colless_index"] == 0
    assert result_df.loc[3, "colless_index"] == 0
    assert result_df.loc[5, "colless_index"] == 0
    assert result_df.loc[6, "colless_index"] == 0

    # Node 4: balanced children (5, 6) -> 0
    assert result_df.loc[4, "colless_index"] == 0

    # Node 2: children 3 (1) and 4 (2) -> |1-2| = 1
    assert result_df.loc[2, "colless_index"] == 1

    # Node 0: children 1 (1) and 2 (3) -> |1-3| = 2, plus subtree (1) = 3
    assert result_df.loc[0, "colless_index"] == 3

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_polytomy_ignored(mutate: bool):
    r"""Test that polytomies (>2 children) have local contribution 0.

          0
        / | \
       1  2  3

    For bifurcating Colless, nodes with != 2 children contribute 0.
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_list": ["[None]", "[0]", "[0]", "[0]"],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_colless_index_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    # Leaves have Colless = 0
    assert result_df.loc[1, "colless_index"] == 0
    assert result_df.loc[2, "colless_index"] == 0
    assert result_df.loc[3, "colless_index"] == 0

    # Root with 3 children -> local contribution = 0 (not bifurcating)
    assert result_df.loc[0, "colless_index"] == 0

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

    Node 3 is bifurcating: |1-1| = 0
    Node 0 has 3 children: local contribution = 0 (not bifurcating)
    Total: 0
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5],
            "ancestor_list": ["[None]", "[0]", "[0]", "[0]", "[3]", "[3]"],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_colless_index_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    # Leaves have Colless = 0
    assert result_df.loc[1, "colless_index"] == 0
    assert result_df.loc[2, "colless_index"] == 0
    assert result_df.loc[4, "colless_index"] == 0
    assert result_df.loc[5, "colless_index"] == 0

    # Node 3: bifurcating with balanced children -> 0
    assert result_df.loc[3, "colless_index"] == 0

    # Node 0: 3 children -> local = 0 (polytomy ignored)
    # Subtree colless from children = 0
    assert result_df.loc[0, "colless_index"] == 0

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
    result_df = alifestd_mark_colless_index_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    # Same structure as test_simple_bifurcating_imbalanced but with non-contiguous IDs
    #       10
    #      /  \
    #    20    30
    #         /  \
    #       40    50

    # Leaves have Colless = 0
    assert result_df.loc[20, "colless_index"] == 0
    assert result_df.loc[40, "colless_index"] == 0
    assert result_df.loc[50, "colless_index"] == 0

    # Node 30 has balanced children -> 0
    assert result_df.loc[30, "colless_index"] == 0

    # Node 10: children 20 (1 leaf) and 30 (2 leaves) -> |1-2| = 1
    assert result_df.loc[10, "colless_index"] == 1

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
    result_df = alifestd_mark_colless_index_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    # Two separate trees, each with one child
    # Both roots have unifurcating structure -> Colless = 0
    assert result_df.loc[0, "colless_index"] == 0
    assert result_df.loc[1, "colless_index"] == 0
    assert result_df.loc[2, "colless_index"] == 0
    assert result_df.loc[3, "colless_index"] == 0

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

    Colless contributions:
    - Node 6: |1-1| = 0
    - Node 4: |1-2| = 1 (children: 5=1, 6=2)
    - Node 2: |1-3| = 2 (children: 3=1, 4=3)
    - Node 0: |1-4| = 3 (children: 1=1, 2=4)

    Total at root: 3 + 2 + 1 + 0 = 6
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
    result_df = alifestd_mark_colless_index_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    # Leaves
    assert result_df.loc[1, "colless_index"] == 0
    assert result_df.loc[3, "colless_index"] == 0
    assert result_df.loc[5, "colless_index"] == 0
    assert result_df.loc[7, "colless_index"] == 0
    assert result_df.loc[8, "colless_index"] == 0

    # Node 6: balanced children 7, 8 -> 0
    assert result_df.loc[6, "colless_index"] == 0

    # Node 4: children 5 (1) and 6 (2) -> |1-2| = 1
    assert result_df.loc[4, "colless_index"] == 1

    # Node 2: children 3 (1) and 4 (3) -> |1-3| = 2, plus subtree = 2 + 1 = 3
    assert result_df.loc[2, "colless_index"] == 3

    # Node 0: children 1 (1) and 2 (4) -> |1-4| = 3, plus subtree = 3 + 3 = 6
    assert result_df.loc[0, "colless_index"] == 6

    if not mutate:
        assert original_df.equals(phylogeny_df)
