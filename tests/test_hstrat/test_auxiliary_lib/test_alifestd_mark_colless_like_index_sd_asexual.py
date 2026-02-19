import math
import os

import pandas as pd
import pytest

from hstrat._auxiliary_lib import (
    alifestd_find_leaf_ids,
    alifestd_find_root_ids,
    alifestd_has_multiple_roots,
    alifestd_make_empty,
    alifestd_mark_colless_like_index_sd_asexual,
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

    result = alifestd_mark_colless_like_index_sd_asexual(phylogeny_df)

    assert alifestd_validate(result)
    assert original.equals(phylogeny_df)

    assert all(result["colless_like_index_sd"] >= 0)

    leaf_ids = [*alifestd_find_leaf_ids(phylogeny_df)]
    for leaf_id in leaf_ids:
        val = result[result["id"] == leaf_id][
            "colless_like_index_sd"
        ].squeeze()
        assert val == 0.0

    if not alifestd_has_multiple_roots(phylogeny_df):
        (root_id,) = alifestd_find_root_ids(phylogeny_df)
        root_val = result[result["id"] == root_id][
            "colless_like_index_sd"
        ].squeeze()
        assert root_val >= 0
        assert root_val == result["colless_like_index_sd"].max()


def test_empty():
    res = alifestd_mark_colless_like_index_sd_asexual(
        alifestd_make_empty(),
    )
    assert "colless_like_index_sd" in res
    assert len(res) == 0


@pytest.mark.parametrize("mutate", [True, False])
def test_simple_chain(mutate: bool):
    """Chain: all unifurcating -> balance = 0."""
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[1]"],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_colless_like_index_sd_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    assert result_df.loc[0, "colless_like_index_sd"] == 0.0
    assert result_df.loc[1, "colless_like_index_sd"] == 0.0
    assert result_df.loc[2, "colless_like_index_sd"] == 0.0

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple_bifurcating_balanced(mutate: bool):
    r"""Balanced bifurcating tree: sd(1, 1) = 0.

          0
         / \
        1   2
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_list": ["[None]", "[0]", "[0]"],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_colless_like_index_sd_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    assert result_df.loc[0, "colless_like_index_sd"] == pytest.approx(
        0.0,
    )
    assert result_df.loc[1, "colless_like_index_sd"] == 0.0
    assert result_df.loc[2, "colless_like_index_sd"] == 0.0

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_simple_bifurcating_imbalanced(mutate: bool):
    r"""Imbalanced bifurcating tree.

          0
         / \
        1   2
           / \
          3   4

    For k=2 values a, b:
        sd = |a - b| / sqrt(2)
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_list": ["[None]", "[0]", "[0]", "[2]", "[2]"],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_colless_like_index_sd_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    assert result_df.loc[1, "colless_like_index_sd"] == 0.0
    assert result_df.loc[3, "colless_like_index_sd"] == 0.0
    assert result_df.loc[4, "colless_like_index_sd"] == 0.0
    assert result_df.loc[2, "colless_like_index_sd"] == pytest.approx(
        0.0,
    )

    # sd(a, b) = |a - b| / sqrt(2)
    fsize_1 = _f(0)
    fsize_2 = _f(2) + 2 * _f(0)
    expected_sd = abs(fsize_2 - fsize_1) / math.sqrt(2)
    assert result_df.loc[0, "colless_like_index_sd"] == pytest.approx(
        expected_sd,
    )

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_polytomy_balanced(mutate: bool):
    r"""Balanced polytomy: sd(1, 1, 1) = 0.

          0
        / | \
       1  2  3
    """
    phylogeny_df = pd.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_list": ["[None]", "[0]", "[0]", "[0]"],
        }
    )
    original_df = phylogeny_df.copy()
    result_df = alifestd_mark_colless_like_index_sd_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    assert result_df.loc[0, "colless_like_index_sd"] == pytest.approx(
        0.0,
    )

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_polytomy_imbalanced(mutate: bool):
    r"""Imbalanced polytomy.

            0
          / | \
         1  2  3
              / \
             4   5

    Children of 0: f-sizes = [1.0, 1.0, ln(2+e)+2.0]
    sd = sqrt(var) = sqrt((1/(3-1)) * sum (x_i - mean)^2)
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
    result_df = alifestd_mark_colless_like_index_sd_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    for leaf in [1, 2, 4, 5]:
        assert result_df.loc[leaf, "colless_like_index_sd"] == 0.0

    assert result_df.loc[3, "colless_like_index_sd"] == pytest.approx(
        0.0,
    )

    fsize_3 = _f(2) + 2 * _f(0)
    vals = [1.0, 1.0, fsize_3]
    mean = sum(vals) / 3
    expected_sd = math.sqrt(sum((v - mean) ** 2 for v in vals) / 2)
    assert result_df.loc[0, "colless_like_index_sd"] == pytest.approx(
        expected_sd,
    )

    if not mutate:
        assert original_df.equals(phylogeny_df)


@pytest.mark.parametrize("mutate", [True, False])
def test_non_contiguous_ids(mutate: bool):
    """Non-contiguous IDs to exercise slow path."""
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
    result_df = alifestd_mark_colless_like_index_sd_asexual(
        phylogeny_df,
        mutate=mutate,
    )
    result_df.index = result_df["id"]

    fsize_20 = _f(0)
    fsize_30 = _f(2) + 2 * _f(0)
    expected_sd = abs(fsize_30 - fsize_20) / math.sqrt(2)
    assert result_df.loc[10, "colless_like_index_sd"] == pytest.approx(
        expected_sd,
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
    result_nc = alifestd_mark_colless_like_index_sd_asexual(
        phylogeny_df_nc,
        mutate=mutate,
    )
    result_c = alifestd_mark_colless_like_index_sd_asexual(
        phylogeny_df_c,
        mutate=mutate,
    )

    result_nc.index = result_nc["id"]
    result_c.index = result_c["id"]
    assert result_nc.loc[10, "colless_like_index_sd"] == pytest.approx(
        result_c.loc[0, "colless_like_index_sd"],
    )


def test_symmetric_tree_is_zero():
    """Fully symmetric trees should have Colless-like sd index 0."""
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
    result_df = alifestd_mark_colless_like_index_sd_asexual(
        phylogeny_df,
    )
    assert result_df["colless_like_index_sd"].to_list() == pytest.approx(
        [0.0] * len(result_df),
    )


def test_relationship_sd_var():
    """sd should be sqrt(var) at every node."""
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
    from hstrat._auxiliary_lib import (
        alifestd_mark_colless_like_index_var_asexual,
    )

    result_sd = alifestd_mark_colless_like_index_sd_asexual(
        phylogeny_df,
    )
    result_var = alifestd_mark_colless_like_index_var_asexual(
        phylogeny_df,
    )

    # For each node the accumulated sd should relate to accumulated
    # var at the root. For a single internal node with k>1 children,
    # sd = sqrt(var). But because these are accumulated (summed),
    # the relationship holds per-node balance, not per accumulated
    # value. Verify at root for this simple tree that has only one
    # non-trivial internal node (node 0).
    result_sd.index = result_sd["id"]
    result_var.index = result_var["id"]

    sd_root = result_sd.loc[0, "colless_like_index_sd"]
    var_root = result_var.loc[0, "colless_like_index_var"]
    assert sd_root == pytest.approx(math.sqrt(var_root))
