import os

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_find_leaf_ids,
    alifestd_find_root_ids,
    alifestd_has_multiple_roots,
    alifestd_make_balanced_bifurcating,
    alifestd_make_comb,
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

    # Root should have the highest or equal Sackin index
    if not alifestd_has_multiple_roots(phylogeny_df):
        (root_id,) = alifestd_find_root_ids(phylogeny_df)
        root_sackin = result[result["id"] == root_id]["sackin_index"].squeeze()
        assert root_sackin >= 0
        # Root sackin should be >= all other nodes' sackin
        assert root_sackin == result["sackin_index"].max()


def test_empty():
    res = alifestd_mark_sackin_index_asexual(alifestd_make_empty())
    assert "sackin_index" in res
    assert len(res) == 0


@pytest.mark.parametrize("mutate", [True, False])
def test_simple_chain(mutate: bool):
    """Test a simple chain/caterpillar tree: 0 -> 1 -> 2.

    Sackin index accumulates through all nodes.
    Node 1: sackin = 0 + 1 = 1 (from leaf 2)
    Node 0: sackin = 1 + 1 = 2 (from node 1)
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

    # Leaf has Sackin = 0
    assert result_df.loc[2, "sackin_index"] == 0

    # Node 1: 0 + 1 = 1
    assert result_df.loc[1, "sackin_index"] == 1

    # Node 0: 1 + 1 = 2
    assert result_df.loc[0, "sackin_index"] == 2

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
def test_polytomy_balanced(mutate: bool):
    r"""Test a tree with balanced polytomy (more than 2 children).

          0
        / | \
       1  2  3

    Sackin index handles polytomies.
    Node 0: (0+1) + (0+1) + (0+1) = 3
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

    # Root with 3 children: (0+1) + (0+1) + (0+1) = 3
    assert result_df.loc[0, "sackin_index"] == 3

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_polytomy_imbalanced(mutate: bool):
    r"""Test a tree with imbalanced polytomy.

            0
          / | \
         1  2  3
              / \
             4   5

    Node 3: (0+1) + (0+1) = 2
    Node 0: (0+1) + (0+1) + (2+2) = 6

    Leaves: 1 (depth 1), 2 (depth 1), 4 (depth 2), 5 (depth 2)
    Total Sackin = 1 + 1 + 2 + 2 = 6
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

    # Node 3: (0+1) + (0+1) = 2
    assert result_df.loc[3, "sackin_index"] == 2

    # Node 0: (0+1) + (0+1) + (2+2) = 6
    assert result_df.loc[0, "sackin_index"] == 6

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_large_polytomy(mutate: bool):
    r"""Test a tree with large polytomy (4 children).

            0
         / | | \
        1  2 3  4

    All leaves at depth 1.
    Node 0: (0+1) + (0+1) + (0+1) + (0+1) = 4
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_list": ["[None]", "[0]", "[0]", "[0]", "[0]"],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_sackin_index_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    # All leaves have Sackin = 0
    assert result_df.loc[1, "sackin_index"] == 0
    assert result_df.loc[2, "sackin_index"] == 0
    assert result_df.loc[3, "sackin_index"] == 0
    assert result_df.loc[4, "sackin_index"] == 0

    # Root with 4 children: 4 * 1 = 4
    assert result_df.loc[0, "sackin_index"] == 4

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_large_polytomy_imbalanced(mutate: bool):
    r"""Test a tree with large imbalanced polytomy.

              0
         / | | \
        1  2 3  4
               / \
              5   6

    Node 4: (0+1) + (0+1) = 2
    Node 0: (0+1) + (0+1) + (0+1) + (2+2) = 7

    Leaves: 1,2,3 (depth 1), 5,6 (depth 2)
    Total Sackin = 1 + 1 + 1 + 2 + 2 = 7
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_list": [
                "[None]",
                "[0]",
                "[0]",
                "[0]",
                "[0]",
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
    assert result_df.loc[2, "sackin_index"] == 0
    assert result_df.loc[3, "sackin_index"] == 0
    assert result_df.loc[5, "sackin_index"] == 0
    assert result_df.loc[6, "sackin_index"] == 0

    # Node 4: (0+1) + (0+1) = 2
    assert result_df.loc[4, "sackin_index"] == 2

    # Node 0: (0+1) + (0+1) + (0+1) + (2+2) = 7
    assert result_df.loc[0, "sackin_index"] == 7

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
def test_non_contiguous_ids_polytomy(mutate: bool):
    """Test polytomy with non-contiguous IDs to exercise slow path."""
    phylogeny_df = pd.DataFrame(
        {
            "id": [10, 20, 30, 40, 50, 60],
            "ancestor_list": [
                "[None]",
                "[10]",
                "[10]",
                "[10]",
                "[40]",
                "[40]",
            ],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_sackin_index_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    # Node 40: (0+1) + (0+1) = 2
    assert result_df.loc[40, "sackin_index"] == 2

    # Node 10: (0+1) + (0+1) + (2+2) = 6
    assert result_df.loc[10, "sackin_index"] == 6

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
    # Generalized handles unifurcations
    assert result_df.loc[2, "sackin_index"] == 0  # leaf
    assert result_df.loc[3, "sackin_index"] == 0  # leaf
    assert result_df.loc[0, "sackin_index"] == 1  # 0 + 1 from child 2
    assert result_df.loc[1, "sackin_index"] == 1  # 0 + 1 from child 3

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


@pytest.mark.parametrize(
    "phylogeny_df, expected_sackin",
    [
        # R treebalance::sackinI and treestats::sackin reference values
        # 2-leaf balanced: (A,B) -> Sackin = 2
        (alifestd_make_balanced_bifurcating(2), 2),
        # 4-leaf balanced: ((A,B),(C,D)) -> Sackin = 8
        (alifestd_make_balanced_bifurcating(3), 8),
        # 8-leaf balanced: (((A,B),(C,D)),((E,F),(G,H))) -> Sackin = 24
        (alifestd_make_balanced_bifurcating(4), 24),
        # 3-leaf caterpillar: (A,(B,C)) -> Sackin = 5
        (alifestd_make_comb(3), 5),
        # 4-leaf caterpillar: (A,(B,(C,D))) -> Sackin = 9
        (alifestd_make_comb(4), 9),
        # 5-leaf caterpillar: (A,(B,(C,(D,E)))) -> Sackin = 14
        (alifestd_make_comb(5), 14),
        # 7-leaf caterpillar -> Sackin = 27
        (alifestd_make_comb(7), 27),
    ],
)
def test_against_r_treebalance_sackin(
    phylogeny_df: pd.DataFrame, expected_sackin: int
):
    """Test Sackin index against values computed with R treebalance::sackinI
    and treestats::sackin packages (both agreed on all values)."""
    result_df = alifestd_mark_sackin_index_asexual(phylogeny_df)
    result_df.index = result_df["id"]
    root_id = result_df[result_df["id"] == result_df["ancestor_id"]][
        "id"
    ].iloc[0]
    assert result_df.loc[root_id, "sackin_index"] == expected_sackin


@pytest.mark.parametrize(
    "phylogeny_df, expected_sackin",
    [
        # R treebalance::sackinI reference values for nontrivial trees
        # (neither purely balanced nor purely comb/caterpillar).
        # ((A,B),(C,(D,E))) -> Sackin = 12
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
            12,
        ),
        # ((A,(B,C)),(D,E)) -> Sackin = 12
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
            12,
        ),
        # (((A,B),C),((D,E),F)) -> Sackin = 16
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
            16,
        ),
        # (((A,B),(C,D)),(E,F)) -> Sackin = 16
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
            16,
        ),
        # ((A,(B,(C,D))),(E,(F,G))) -> Sackin = 21
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
            21,
        ),
        # (((A,B),(C,(D,E))),((F,G),(H,I))) -> Sackin = 29
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
            29,
        ),
        # ((A,B),((C,D),((E,F),(G,H)))) -> Sackin = 26
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
            26,
        ),
        # Polytomy: (A,B,(C,(D,E))) -> Sackin = 10
        (
            pd.DataFrame(
                {
                    "id": range(8),
                    "ancestor_list": [
                        "[None]",
                        "[0]",
                        "[0]",
                        "[0]",
                        "[3]",
                        "[3]",
                        "[5]",
                        "[5]",
                    ],
                }
            ),
            10,
        ),
        # Polytomy: ((A,B,C),(D,(E,F))) -> Sackin = 14
        (
            pd.DataFrame(
                {
                    "id": range(10),
                    "ancestor_list": [
                        "[None]",
                        "[0]",
                        "[0]",
                        "[1]",
                        "[1]",
                        "[1]",
                        "[2]",
                        "[2]",
                        "[7]",
                        "[7]",
                    ],
                }
            ),
            14,
        ),
    ],
)
def test_against_r_nontrivial_trees_sackin(
    phylogeny_df: pd.DataFrame, expected_sackin: int
):
    """Test Sackin index against R treebalance::sackinI values for nontrivial
    trees (neither purely balanced nor purely comb/caterpillar)."""
    result_df = alifestd_mark_sackin_index_asexual(phylogeny_df)
    result_df.index = result_df["id"]
    root_id = result_df[result_df["id"] == result_df["ancestor_id"]][
        "id"
    ].iloc[0]
    assert result_df.loc[root_id, "sackin_index"] == expected_sackin
