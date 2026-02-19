import os

import numpy as np
import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_find_leaf_ids,
    alifestd_find_root_ids,
    alifestd_has_multiple_roots,
    alifestd_is_strictly_bifurcating_asexual,
    alifestd_make_balanced_bifurcating,
    alifestd_make_comb,
    alifestd_make_empty,
    alifestd_mark_colless_index_asexual,
    alifestd_mark_num_leaves_asexual,
    alifestd_try_add_ancestor_id_col,
    alifestd_validate,
)
from hstrat._auxiliary_lib._alifestd_mark_colless_index_asexual import (
    alifestd_mark_colless_index_asexual_fast_path,
    alifestd_mark_colless_index_asexual_slow_path,
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
            alifestd_mark_colless_index_asexual(phylogeny_df)
        return

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


def test_simple_chain_raises():
    """Test a simple chain/caterpillar tree: 0 -> 1 -> 2.

    Unifurcating chain is not strictly bifurcating, should raise ValueError.
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[1]"],
        }
    )
    with pytest.raises(ValueError, match="strictly bifurcating"):
        alifestd_mark_colless_index_asexual(phylogeny_df)


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


def test_polytomy_raises():
    r"""Test that polytomies (>2 children) raise ValueError.

          0
        / | \
       1  2  3

    Polytomies are not strictly bifurcating, should raise ValueError.
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_list": ["[None]", "[0]", "[0]", "[0]"],
        }
    )
    with pytest.raises(ValueError, match="strictly bifurcating"):
        alifestd_mark_colless_index_asexual(phylogeny_df)


def test_polytomy_with_bifurcating_subtree_raises():
    r"""Test tree with polytomy at root raises ValueError.

            0
          / | \
         1  2  3
              / \
             4   5

    Tree has polytomy at root, should raise ValueError.
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5],
            "ancestor_list": ["[None]", "[0]", "[0]", "[0]", "[3]", "[3]"],
        }
    )
    with pytest.raises(ValueError, match="strictly bifurcating"):
        alifestd_mark_colless_index_asexual(phylogeny_df)


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


def test_multiple_roots_unifurcating_raises():
    """Test with multiple roots (forest) with unifurcating structure raises."""
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_list": ["[None]", "[None]", "[0]", "[1]"],
        }
    )
    # Unifurcating roots are not strictly bifurcating
    with pytest.raises(ValueError, match="strictly bifurcating"):
        alifestd_mark_colless_index_asexual(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_multiple_roots_bifurcating(mutate: bool):
    """Test with multiple roots (forest) where each tree is bifurcating."""
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5],
            "ancestor_list": ["[None]", "[None]", "[0]", "[0]", "[1]", "[1]"],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_colless_index_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    # Two separate balanced bifurcating trees
    # Each root has 2 children with 1 leaf each -> |1-1| = 0
    assert result_df.loc[0, "colless_index"] == 0
    assert result_df.loc[1, "colless_index"] == 0
    assert result_df.loc[2, "colless_index"] == 0
    assert result_df.loc[3, "colless_index"] == 0
    assert result_df.loc[4, "colless_index"] == 0
    assert result_df.loc[5, "colless_index"] == 0

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


@pytest.mark.parametrize(
    "phylogeny_df, expected_colless",
    [
        # R treebalance::collessI(, "original") and treestats::colless
        # reference values
        # 2-leaf balanced: (A,B) -> Colless = 0
        (alifestd_make_balanced_bifurcating(2), 0),
        # 4-leaf balanced: ((A,B),(C,D)) -> Colless = 0
        (alifestd_make_balanced_bifurcating(3), 0),
        # 8-leaf balanced -> Colless = 0
        (alifestd_make_balanced_bifurcating(4), 0),
        # 3-leaf caterpillar: (A,(B,C)) -> Colless = 1
        (alifestd_make_comb(3), 1),
        # 4-leaf caterpillar: (A,(B,(C,D))) -> Colless = 3
        (alifestd_make_comb(4), 3),
        # 5-leaf caterpillar -> Colless = 6
        (alifestd_make_comb(5), 6),
        # 7-leaf caterpillar -> Colless = 15
        (alifestd_make_comb(7), 15),
    ],
)
def test_against_r_treebalance_colless(
    phylogeny_df: pd.DataFrame, expected_colless: int
):
    """Test Colless index against values computed with R
    treebalance::collessI(, "original") and treestats::colless packages
    (both agreed on all values)."""
    result_df = alifestd_mark_colless_index_asexual(phylogeny_df)
    result_df.index = result_df["id"]
    root_id = result_df[result_df["id"] == result_df["ancestor_id"]][
        "id"
    ].iloc[0]
    assert result_df.loc[root_id, "colless_index"] == expected_colless


@pytest.mark.parametrize(
    "phylogeny_df, expected_colless",
    [
        # R treebalance::collessI(, "original") reference values for
        # nontrivial bifurcating trees.
        # ((A,B),(C,(D,E))) -> Colless = 2
        (
            pd.DataFrame(
                {
                    "id": range(9),
                    "ancestor_list": [
                        "[None]",
                        "[0]",
                        "[0]",
                        "[1]",
                        "[1]",
                        "[2]",
                        "[2]",
                        "[6]",
                        "[6]",
                    ],
                }
            ),
            2,
        ),
        # ((A,(B,C)),(D,E)) -> Colless = 2
        (
            pd.DataFrame(
                {
                    "id": range(9),
                    "ancestor_list": [
                        "[None]",
                        "[0]",
                        "[0]",
                        "[1]",
                        "[1]",
                        "[2]",
                        "[2]",
                        "[4]",
                        "[4]",
                    ],
                }
            ),
            2,
        ),
        # (((A,B),C),((D,E),F)) -> Colless = 2
        (
            pd.DataFrame(
                {
                    "id": range(11),
                    "ancestor_list": [
                        "[None]",
                        "[0]",
                        "[0]",
                        "[1]",
                        "[1]",
                        "[2]",
                        "[2]",
                        "[3]",
                        "[3]",
                        "[5]",
                        "[5]",
                    ],
                }
            ),
            2,
        ),
        # (((A,B),(C,D)),(E,F)) -> Colless = 2
        (
            pd.DataFrame(
                {
                    "id": range(11),
                    "ancestor_list": [
                        "[None]",
                        "[0]",
                        "[0]",
                        "[1]",
                        "[1]",
                        "[2]",
                        "[2]",
                        "[3]",
                        "[3]",
                        "[4]",
                        "[4]",
                    ],
                }
            ),
            2,
        ),
        # ((A,(B,(C,D))),(E,(F,G))) -> Colless = 5
        (
            pd.DataFrame(
                {
                    "id": range(13),
                    "ancestor_list": [
                        "[None]",
                        "[0]",
                        "[0]",
                        "[1]",
                        "[1]",
                        "[2]",
                        "[2]",
                        "[4]",
                        "[4]",
                        "[6]",
                        "[6]",
                        "[8]",
                        "[8]",
                    ],
                }
            ),
            5,
        ),
        # (((A,B),(C,(D,E))),((F,G),(H,I))) -> Colless = 3
        (
            pd.DataFrame(
                {
                    "id": range(17),
                    "ancestor_list": [
                        "[None]",
                        "[0]",
                        "[0]",
                        "[1]",
                        "[1]",
                        "[2]",
                        "[2]",
                        "[3]",
                        "[3]",
                        "[4]",
                        "[4]",
                        "[5]",
                        "[5]",
                        "[6]",
                        "[6]",
                        "[10]",
                        "[10]",
                    ],
                }
            ),
            3,
        ),
        # ((A,B),((C,D),((E,F),(G,H)))) -> Colless = 6
        (
            pd.DataFrame(
                {
                    "id": range(15),
                    "ancestor_list": [
                        "[None]",
                        "[0]",
                        "[0]",
                        "[1]",
                        "[1]",
                        "[2]",
                        "[2]",
                        "[5]",
                        "[5]",
                        "[6]",
                        "[6]",
                        "[9]",
                        "[9]",
                        "[10]",
                        "[10]",
                    ],
                }
            ),
            6,
        ),
    ],
)
def test_against_r_nontrivial_trees_colless(
    phylogeny_df: pd.DataFrame, expected_colless: int
):
    """Test Colless index against R treebalance::collessI(, "original")
    values for nontrivial bifurcating trees."""
    result_df = alifestd_mark_colless_index_asexual(phylogeny_df)
    result_df.index = result_df["id"]
    root_id = result_df[result_df["id"] == result_df["ancestor_id"]][
        "id"
    ].iloc[0]
    assert result_df.loc[root_id, "colless_index"] == expected_colless


def test_fast_slow_path_direct_comparison():
    """Directly call fast and slow paths and compare results."""
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
    phylogeny_df = alifestd_try_add_ancestor_id_col(
        phylogeny_df,
        mutate=True,
    )
    phylogeny_df = alifestd_mark_num_leaves_asexual(
        phylogeny_df,
        mutate=True,
    )

    fast_result = alifestd_mark_colless_index_asexual_fast_path(
        phylogeny_df["ancestor_id"].to_numpy(),
        phylogeny_df["num_leaves"].to_numpy(),
    )
    slow_result = alifestd_mark_colless_index_asexual_slow_path(
        phylogeny_df.copy(),
    )

    np.testing.assert_array_equal(fast_result, slow_result)
