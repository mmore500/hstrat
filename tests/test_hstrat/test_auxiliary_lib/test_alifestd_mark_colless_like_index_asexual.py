import math
import os

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_find_leaf_ids,
    alifestd_find_root_ids,
    alifestd_has_multiple_roots,
    alifestd_make_empty,
    alifestd_mark_colless_like_index_asexual,
    alifestd_validate,
)

assets_path = os.path.join(os.path.dirname(__file__), "assets")


def _f(k):
    """Weight function f(k) = ln(k + e)."""
    return math.log(k + math.e)


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

    result = alifestd_mark_colless_like_index_asexual(phylogeny_df)

    assert alifestd_validate(result)
    assert original.equals(phylogeny_df)

    # Colless-like index should be non-negative
    assert all(result["colless_like_index"] >= 0)

    # Leaf nodes should have Colless-like index 0
    leaf_ids = [*alifestd_find_leaf_ids(phylogeny_df)]
    for leaf_id in leaf_ids:
        val = result[result["id"] == leaf_id]["colless_like_index"].squeeze()
        assert val == 0.0

    # Root should have the highest or equal index
    if not alifestd_has_multiple_roots(phylogeny_df):
        (root_id,) = alifestd_find_root_ids(phylogeny_df)
        root_val = result[result["id"] == root_id][
            "colless_like_index"
        ].squeeze()
        assert root_val >= 0
        assert root_val == result["colless_like_index"].max()


def test_empty():
    res = alifestd_mark_colless_like_index_asexual(
        alifestd_make_empty(),
    )
    assert "colless_like_index" in res
    assert len(res) == 0


@pytest.mark.parametrize("mutate", [True, False])
def test_simple_chain(mutate: bool):
    """Test a simple chain: 0 -> 1 -> 2.

    All nodes are unifurcating (<=1 child), so balance = 0.
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[1]"],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_colless_like_index_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    assert result_df.loc[0, "colless_like_index"] == 0.0
    assert result_df.loc[1, "colless_like_index"] == 0.0
    assert result_df.loc[2, "colless_like_index"] == 0.0

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple_bifurcating_balanced(mutate: bool):
    r"""Test a balanced bifurcating tree.

          0
         / \
        1   2

    Both children are leaves with identical f-size = f(0) = ln(e) = 1.
    MDM(1, 1) = 0.  So index at root = 0.
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[0]"],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_colless_like_index_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    assert result_df.loc[0, "colless_like_index"] == pytest.approx(0.0)
    assert result_df.loc[1, "colless_like_index"] == 0.0
    assert result_df.loc[2, "colless_like_index"] == 0.0

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

    f-sizes:
    - Leaf (deg 0): f(0) = ln(e) = 1.0
    - Node 2 (deg 2): f(2) + f_size(3) + f_size(4)
                     = ln(2+e) + 1.0 + 1.0 = ln(2+e) + 2.0
    - Node 1 (leaf): f_size = 1.0

    Node 2 balance: children 3, 4 have equal f-sizes (1.0, 1.0)
                    MDM(1,1) = 0
    Node 0 balance: children have f-sizes 1.0 and ln(2+e)+2.0
                    diff = ln(2+e) + 1.0
                    MDM = (1/2) * (diff/2 + diff/2) = diff/2
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_list": ["[None]", "[0]", "[0]", "[2]", "[2]"],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_colless_like_index_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    # Leaves have index 0
    assert result_df.loc[1, "colless_like_index"] == 0.0
    assert result_df.loc[3, "colless_like_index"] == 0.0
    assert result_df.loc[4, "colless_like_index"] == 0.0

    # Node 2: balanced children -> 0
    assert result_df.loc[2, "colless_like_index"] == pytest.approx(0.0)

    # Node 0: MDM of (1.0, ln(2+e)+2.0)
    fsize_1 = _f(0)  # 1.0
    fsize_2 = _f(2) + 2 * _f(0)  # ln(2+e) + 2.0
    diff = abs(fsize_2 - fsize_1)
    expected_bal = diff / 2.0  # MDM of two values
    assert result_df.loc[0, "colless_like_index"] == pytest.approx(
        expected_bal,
    )

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_polytomy_balanced(mutate: bool):
    r"""Test a tree with balanced polytomy.

          0
        / | \
       1  2  3

    All children are leaves with f-size = 1.0.
    MDM(1, 1, 1) = 0. Index at root = 0.
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_list": ["[None]", "[0]", "[0]", "[0]"],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_colless_like_index_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    assert result_df.loc[1, "colless_like_index"] == 0.0
    assert result_df.loc[2, "colless_like_index"] == 0.0
    assert result_df.loc[3, "colless_like_index"] == 0.0
    assert result_df.loc[0, "colless_like_index"] == pytest.approx(0.0)

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

    f-sizes:
    - Leaves 1, 2, 4, 5: f(0) = 1.0
    - Node 3: f(2) + 1.0 + 1.0 = ln(2+e) + 2.0
    - Children of 0: 1.0, 1.0, ln(2+e)+2.0

    Sorted children f-sizes: [1.0, 1.0, ln(2+e)+2.0]
    Median = 1.0 (middle value of 3)
    MDM = (1/3) * (|1-1| + |1-1| + |ln(2+e)+2-1|)
        = (1/3) * (ln(2+e) + 1.0)
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5],
            "ancestor_list": [
                "[None]",
                "[0]",
                "[0]",
                "[0]",
                "[3]",
                "[3]",
            ],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_colless_like_index_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    # Leaves
    for leaf in [1, 2, 4, 5]:
        assert result_df.loc[leaf, "colless_like_index"] == 0.0

    # Node 3: balanced children -> 0
    assert result_df.loc[3, "colless_like_index"] == pytest.approx(0.0)

    # Node 0: MDM of [1.0, 1.0, ln(2+e)+2.0], median=1.0
    fsize_3 = _f(2) + 2 * _f(0)
    expected_bal = (abs(1.0 - 1.0) + abs(1.0 - 1.0) + abs(fsize_3 - 1.0)) / 3
    assert result_df.loc[0, "colless_like_index"] == pytest.approx(
        expected_bal,
    )

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_non_contiguous_ids(mutate: bool):
    """Test with non-contiguous IDs to exercise slow path."""
    phylogeny_df = pd.DataFrame(
        {
            "id": [10, 20, 30, 40, 50],
            "ancestor_list": [
                "[None]",
                "[10]",
                "[10]",
                "[30]",
                "[30]",
            ],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_colless_like_index_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    # Same structure as test_simple_bifurcating_imbalanced
    # Leaves
    assert result_df.loc[20, "colless_like_index"] == 0.0
    assert result_df.loc[40, "colless_like_index"] == 0.0
    assert result_df.loc[50, "colless_like_index"] == 0.0

    # Node 30: balanced -> 0
    assert result_df.loc[30, "colless_like_index"] == pytest.approx(0.0)

    # Root 10: same expected value as imbalanced test
    fsize_20 = _f(0)
    fsize_30 = _f(2) + 2 * _f(0)
    diff = abs(fsize_30 - fsize_20)
    expected_bal = diff / 2.0
    assert result_df.loc[10, "colless_like_index"] == pytest.approx(
        expected_bal,
    )

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_non_contiguous_ids_polytomy(mutate: bool):
    """Test polytomy with non-contiguous IDs."""
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
    result_df = alifestd_mark_colless_like_index_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    # Same structure as polytomy_imbalanced but shifted IDs
    fsize_40 = _f(2) + 2 * _f(0)
    expected_bal = (abs(1.0 - 1.0) + abs(1.0 - 1.0) + abs(fsize_40 - 1.0)) / 3
    assert result_df.loc[10, "colless_like_index"] == pytest.approx(
        expected_bal,
    )

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
    result_df = alifestd_mark_colless_like_index_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    # Two trees, each unifurcating -> all 0
    assert result_df.loc[0, "colless_like_index"] == 0.0
    assert result_df.loc[1, "colless_like_index"] == 0.0
    assert result_df.loc[2, "colless_like_index"] == 0.0
    assert result_df.loc[3, "colless_like_index"] == 0.0

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_fast_slow_path_agreement(mutate: bool):
    """Fast and slow paths should produce the same values."""
    # Non-contiguous version of an imbalanced tree
    phylogeny_df_nc = pd.DataFrame(
        {
            "id": [10, 20, 30, 40, 50, 60, 70],
            "ancestor_list": [
                "[None]",
                "[10]",
                "[10]",
                "[10]",
                "[10]",
                "[50]",
                "[50]",
            ],
        }
    )
    # Contiguous version of the same tree
    phylogeny_df_c = pd.DataFrame(
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
    result_nc = alifestd_mark_colless_like_index_asexual(
        phylogeny_df_nc,
        mutate=mutate,
    )
    result_c = alifestd_mark_colless_like_index_asexual(
        phylogeny_df_c,
        mutate=mutate,
    )

    # Root values should match
    result_nc.index = result_nc["id"]
    result_c.index = result_c["id"]
    assert result_nc.loc[10, "colless_like_index"] == pytest.approx(
        result_c.loc[0, "colless_like_index"],
    )


def test_symmetric_tree_is_zero():
    """Fully symmetric trees should have Colless-like index 0.

    This is the key property that makes the index "sound" per
    Mir et al. 2018.
    """
    # Symmetric bifurcating tree with 4 leaves
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
    result_df = alifestd_mark_colless_like_index_asexual(phylogeny_df)
    assert result_df["colless_like_index"].to_list() == pytest.approx(
        [0.0] * len(result_df),
    )

    # Symmetric trifurcating tree (3 leaves)
    phylogeny_df2 = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_list": ["[None]", "[0]", "[0]", "[0]"],
        }
    )
    result_df2 = alifestd_mark_colless_like_index_asexual(
        phylogeny_df2,
    )
    assert result_df2["colless_like_index"].to_list() == pytest.approx(
        [0.0] * len(result_df2),
    )
