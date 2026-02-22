import math
import os

import numpy as np
import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_find_leaf_ids,
    alifestd_find_root_ids,
    alifestd_has_multiple_roots,
    alifestd_make_balanced_bifurcating,
    alifestd_make_comb,
    alifestd_make_empty,
    alifestd_mark_colless_like_index_mdm_asexual,
    alifestd_mark_num_children_asexual,
    alifestd_try_add_ancestor_id_col,
    alifestd_validate,
)
from hstrat._auxiliary_lib._alifestd_mark_colless_like_index_mdm_asexual import (
    _colless_like_fast_path,
    _colless_like_slow_path,
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

    result = alifestd_mark_colless_like_index_mdm_asexual(phylogeny_df)

    assert alifestd_validate(result)
    assert original.equals(phylogeny_df)

    # Colless-like index should be non-negative
    assert all(result["colless_like_index_mdm"] >= 0)

    # Leaf nodes should have Colless-like index 0
    leaf_ids = [*alifestd_find_leaf_ids(phylogeny_df)]
    for leaf_id in leaf_ids:
        val = result[result["id"] == leaf_id][
            "colless_like_index_mdm"
        ].squeeze()
        assert val == 0.0

    # Root should have the highest or equal index
    if not alifestd_has_multiple_roots(phylogeny_df):
        (root_id,) = alifestd_find_root_ids(phylogeny_df)
        root_val = result[result["id"] == root_id][
            "colless_like_index_mdm"
        ].squeeze()
        assert root_val >= 0
        assert root_val == result["colless_like_index_mdm"].max()


def test_empty():
    res = alifestd_mark_colless_like_index_mdm_asexual(
        alifestd_make_empty(),
    )
    assert "colless_like_index_mdm" in res
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
    result_df = alifestd_mark_colless_like_index_mdm_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    assert result_df.loc[0, "colless_like_index_mdm"] == 0.0
    assert result_df.loc[1, "colless_like_index_mdm"] == 0.0
    assert result_df.loc[2, "colless_like_index_mdm"] == 0.0

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
    result_df = alifestd_mark_colless_like_index_mdm_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    assert result_df.loc[0, "colless_like_index_mdm"] == pytest.approx(
        0.0,
    )
    assert result_df.loc[1, "colless_like_index_mdm"] == 0.0
    assert result_df.loc[2, "colless_like_index_mdm"] == 0.0

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
    result_df = alifestd_mark_colless_like_index_mdm_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    # Leaves have index 0
    assert result_df.loc[1, "colless_like_index_mdm"] == 0.0
    assert result_df.loc[3, "colless_like_index_mdm"] == 0.0
    assert result_df.loc[4, "colless_like_index_mdm"] == 0.0

    # Node 2: balanced children -> 0
    assert result_df.loc[2, "colless_like_index_mdm"] == pytest.approx(
        0.0,
    )

    # Node 0: MDM of (1.0, ln(2+e)+2.0)
    fsize_1 = math.log(0 + math.e)  # 1.0
    fsize_2 = math.log(2 + math.e) + 2 * math.log(0 + math.e)  # ln(2+e) + 2.0
    diff = abs(fsize_2 - fsize_1)
    expected_bal = diff / 2.0  # MDM of two values
    assert result_df.loc[0, "colless_like_index_mdm"] == pytest.approx(
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
    result_df = alifestd_mark_colless_like_index_mdm_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    assert result_df.loc[1, "colless_like_index_mdm"] == 0.0
    assert result_df.loc[2, "colless_like_index_mdm"] == 0.0
    assert result_df.loc[3, "colless_like_index_mdm"] == 0.0
    assert result_df.loc[0, "colless_like_index_mdm"] == pytest.approx(
        0.0,
    )

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
    result_df = alifestd_mark_colless_like_index_mdm_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    # Leaves
    for leaf in [1, 2, 4, 5]:
        assert result_df.loc[leaf, "colless_like_index_mdm"] == 0.0

    # Node 3: balanced children -> 0
    assert result_df.loc[3, "colless_like_index_mdm"] == pytest.approx(
        0.0,
    )

    # Node 0: MDM of [1.0, 1.0, ln(2+e)+2.0], median=1.0
    fsize_3 = math.log(2 + math.e) + 2 * math.log(0 + math.e)
    expected_bal = (abs(1.0 - 1.0) + abs(1.0 - 1.0) + abs(fsize_3 - 1.0)) / 3
    assert result_df.loc[0, "colless_like_index_mdm"] == pytest.approx(
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
    result_df = alifestd_mark_colless_like_index_mdm_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    # Same structure as test_simple_bifurcating_imbalanced
    assert result_df.loc[20, "colless_like_index_mdm"] == 0.0
    assert result_df.loc[40, "colless_like_index_mdm"] == 0.0
    assert result_df.loc[50, "colless_like_index_mdm"] == 0.0
    assert result_df.loc[30, "colless_like_index_mdm"] == pytest.approx(
        0.0,
    )

    fsize_20 = math.log(0 + math.e)
    fsize_30 = math.log(2 + math.e) + 2 * math.log(0 + math.e)
    diff = abs(fsize_30 - fsize_20)
    expected_bal = diff / 2.0
    assert result_df.loc[10, "colless_like_index_mdm"] == pytest.approx(
        expected_bal,
    )

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_fast_slow_path_agreement(mutate: bool):
    """Fast and slow paths should produce the same values."""
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
    result_nc = alifestd_mark_colless_like_index_mdm_asexual(
        phylogeny_df_nc,
        mutate=mutate,
    )
    result_c = alifestd_mark_colless_like_index_mdm_asexual(
        phylogeny_df_c,
        mutate=mutate,
    )

    result_nc.index = result_nc["id"]
    result_c.index = result_c["id"]
    assert result_nc.loc[10, "colless_like_index_mdm"] == pytest.approx(
        result_c.loc[0, "colless_like_index_mdm"],
    )


def test_symmetric_tree_is_zero():
    """Fully symmetric trees should have Colless-like index 0."""
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
    result_df = alifestd_mark_colless_like_index_mdm_asexual(
        phylogeny_df,
    )
    assert result_df["colless_like_index_mdm"].to_list() == pytest.approx(
        [0.0] * len(result_df),
    )

    # Symmetric trifurcating tree (3 leaves)
    phylogeny_df2 = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_list": ["[None]", "[0]", "[0]", "[0]"],
        }
    )
    result_df2 = alifestd_mark_colless_like_index_mdm_asexual(
        phylogeny_df2,
    )
    assert result_df2["colless_like_index_mdm"].to_list() == pytest.approx(
        [0.0] * len(result_df2),
    )


@pytest.mark.parametrize(
    "phylogeny_df, expected_cl",
    [
        (alifestd_make_balanced_bifurcating(2), 0.0),
        (alifestd_make_balanced_bifurcating(3), 0.0),
        (alifestd_make_balanced_bifurcating(4), 0.0),
        (alifestd_make_comb(3), 2.551444713932051 / 2),
        (alifestd_make_comb(4), 7.654334141796154 / 2),
        (alifestd_make_comb(5), 15.308668283592308 / 2),
    ],
)
def test_against_r_treebalance_colless_like(
    phylogeny_df: pd.DataFrame, expected_cl: float
):
    """Test Colless-like index against values derived from R
    treebalance::collesslikeI(, f.size="ln", dissim="mdm").

    Note: R treebalance 1.0.x has an operator precedence bug in its MDM
    dissimilarity where ``return(sum(abs(x - median(x))))/length(x)``
    puts the division outside the return, computing sum instead of mean
    absolute deviation from median. For bifurcating trees (all nodes
    k=2), the R values are exactly 2x the correct MDM values, so we
    divide by 2 to get the correct expected values per Mir et al. (2018).
    """
    result_df = alifestd_mark_colless_like_index_mdm_asexual(phylogeny_df)
    result_df.index = result_df["id"]
    root_id = result_df[result_df["id"] == result_df["ancestor_id"]][
        "id"
    ].iloc[0]
    assert result_df.loc[root_id, "colless_like_index_mdm"] == pytest.approx(
        expected_cl,
    )


def test_colless_like_trifurcation_mixed():
    """Test Colless-like index for a tree with trifurcation.

    Correct MDM at root: children f-sizes = [1.0, 1.0, ln(2+e)+2.0]
    Median = 1.0 (middle of 3 sorted values)
    MDM = (1/3) * (0 + 0 + |ln(2+e)+2.0 - 1.0|) = (ln(2+e)+1.0)/3
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
    result_df = alifestd_mark_colless_like_index_mdm_asexual(phylogeny_df)
    result_df.index = result_df["id"]

    r_buggy_value = 2.551444713932051
    expected_root = r_buggy_value / 3.0
    assert result_df.loc[0, "colless_like_index_mdm"] == pytest.approx(
        expected_root,
    )


@pytest.mark.parametrize(
    "phylogeny_df, expected_cl",
    [
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
            2.5514447139320513,
        ),
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
            2.5514447139320513,
        ),
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
            2.5514447139320513,
        ),
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
            2.5514447139320513,
        ),
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
            6.378611784830128,
        ),
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
            3.827167070898077,
        ),
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
            7.654334141796154,
        ),
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
            2.976685499587393,
        ),
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
            1.955332880583737,
        ),
    ],
)
def test_against_r_nontrivial_trees_colless_like(
    phylogeny_df: pd.DataFrame, expected_cl: float
):
    """Test Colless-like index against values derived from R
    treebalance::collesslikeI for nontrivial trees, corrected for the
    R MDM bug."""
    result_df = alifestd_mark_colless_like_index_mdm_asexual(phylogeny_df)
    result_df.index = result_df["id"]
    root_id = result_df[result_df["id"] == result_df["ancestor_id"]][
        "id"
    ].iloc[0]
    assert result_df.loc[root_id, "colless_like_index_mdm"] == pytest.approx(
        expected_cl,
    )


def test_fast_slow_path_direct_comparison():
    """Directly call fast and slow paths and compare results."""
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
    phylogeny_df = alifestd_try_add_ancestor_id_col(
        phylogeny_df,
        mutate=True,
    )
    phylogeny_df = alifestd_mark_num_children_asexual(
        phylogeny_df,
        mutate=True,
    )
    fast_result = _colless_like_fast_path(
        phylogeny_df["ancestor_id"].to_numpy(),
        0,
    )
    slow_result = _colless_like_slow_path(phylogeny_df.copy(), "mdm")

    np.testing.assert_allclose(fast_result, slow_result)
