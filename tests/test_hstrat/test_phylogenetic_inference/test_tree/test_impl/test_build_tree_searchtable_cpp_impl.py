import numpy as np
import polars as pl
from tqdm import tqdm

from hstrat._auxiliary_lib import (
    alifestd_is_chronologically_ordered,
    alifestd_try_add_ancestor_list_col,
    alifestd_validate,
)
from hstrat.phylogenetic_inference.tree._impl._build_tree_searchtable_cpp_impl_stub import (
    Records,
    build_tree_searchtable_cpp_from_exploded,
    collapse_unifurcations,
    copy_records_to_dict,
    placeholder_value,
)


def test_collapse_unifurcations_singleton():
    records = Records(1)
    records = collapse_unifurcations(records, dropped_only=False)
    assert len(records) == 1


def test_collapse_all_unifurcations_linear_tree():
    # 0 <- 1 <- 2 <- 3 <- 4 <- 5 <- 6 <- 7
    records = Records(8)
    records.addRecord(1, 1, 0, 0, 2, 1, 1, 1, 1)
    records.addRecord(2, 2, 1, 1, 3, 2, 2, 2, 2)
    records.addRecord(3, 3, 2, 2, 4, 3, 3, 3, 3)
    records.addRecord(4, 4, 3, 3, 5, 4, 4, 4, 4)
    records.addRecord(5, 5, 4, 4, 6, 5, 5, 5, 5)
    records.addRecord(6, 6, 5, 5, 7, 6, 6, 6, 6)
    records.addRecord(7, 7, 6, 6, 7, 7, 7, 7, 7)

    records = collapse_unifurcations(records, dropped_only=False)
    assert len(records) == 2

    result = copy_records_to_dict(records)

    # 0 <- 7(1)
    expected = {
        "dstream_data_id": [placeholder_value, 7],
        "id": [0, 1],
        "ancestor_id": [0, 0],
        "search_ancestor_id": [placeholder_value] * 2,
        "search_first_child_id": [placeholder_value] * 2,
        "search_prev_sibling_id": [placeholder_value] * 2,
        "search_next_sibling_id": [placeholder_value] * 2,
        "rank": [0, 7],
        "differentia": [0, 7],
    }

    for key in expected:
        expected_value = expected[key]
        assert result[key] == expected_value, key


def test_collapse_all_unifurcations_branched_tree():
    # 0 <- 1 <- 3
    #  \ <- 2 <- 4 <- 5 <- 6
    #                  \ <- 7
    records = Records(8)
    records.addRecord(1, 1, 0, 0, 3, 1, 2, 1, 1)
    records.addRecord(2, 2, 0, 0, 4, 1, 2, 1, 2)
    records.addRecord(3, 3, 1, 1, 3, 3, 3, 2, 1)
    records.addRecord(4, 4, 2, 2, 5, 4, 4, 2, 1)
    records.addRecord(5, 5, 4, 4, 5, 5, 5, 3, 0)
    records.addRecord(6, 6, 5, 5, 6, 6, 7, 4, 1)
    records.addRecord(7, 7, 5, 5, 7, 6, 7, 4, 2)
    records = collapse_unifurcations(records, dropped_only=False)
    assert len(records) == 5

    result = copy_records_to_dict(records)

    # 0 <- 3(1)
    #  \ <- 5(2) <- 6(3)
    #         \  <- 7(4)
    expected = {
        "dstream_data_id": [placeholder_value, 3, 5, 6, 7],
        "id": [0, 1, 2, 3, 4],
        "ancestor_id": [0, 0, 0, 2, 2],
        "search_ancestor_id": [placeholder_value] * 5,
        "search_first_child_id": [placeholder_value] * 5,
        "search_prev_sibling_id": [placeholder_value] * 5,
        "search_next_sibling_id": [placeholder_value] * 5,
        "rank": [0, 2, 3, 4, 4],
        "differentia": [0, 1, 0, 1, 2],
    }

    for key, value in result.items():
        expected_value = expected[key]
        assert value == expected_value, key


def test_regression_original():
    exploded = pl.DataFrame(
        {
            "dstream_data_id": pl.Series(
                "dstream_data_id",
                [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
                dtype=pl.UInt64,
            ),
            "dstream_T": pl.Series(
                "dstream_T",
                [8, 8, 8, 8, 8, 8, 8, 8, 11, 11, 11, 11, 11, 11, 11, 11],
                dtype=pl.UInt64,
            ),
            "dstream_value_bitwidth": pl.Series(
                "dstream_value_bitwidth",
                [8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8],
                dtype=pl.UInt32,
            ),
            "dstream_value": pl.Series(
                "dstream_value",
                [0, 1, 3, 7, 2, 5, 4, 6, 0, 1, 3, 7, 2, 5, 9, 6],
                dtype=pl.UInt64,
            ),
            "dstream_Tbar": pl.Series(
                "dstream_Tbar",
                [0, 1, 3, 7, 2, 5, 4, 6, 0, 1, 3, 7, 2, 5, 9, 6],
                dtype=pl.UInt64,
            ),
        },
    ).select(
        pl.col(
            "dstream_data_id",
            "dstream_T",
            "dstream_Tbar",
            "dstream_value",
        )
        .sort_by("dstream_Tbar")
        .over(partition_by="dstream_data_id"),
    )
    res = build_tree_searchtable_cpp_from_exploded(
        exploded["dstream_data_id"].to_numpy(),
        exploded["dstream_T"].to_numpy(),
        exploded["dstream_Tbar"].to_numpy(),
        exploded["dstream_value"].to_numpy(),
        tqdm,
    )
    res = pl.DataFrame(res)
    assert alifestd_validate(
        alifestd_try_add_ancestor_list_col(res.to_pandas()),
    )
    assert alifestd_is_chronologically_ordered(
        alifestd_try_add_ancestor_list_col(
            res.with_columns(origin_time=pl.col("rank")).to_pandas(),
        ),
    )


def test_regression_distilled():
    exploded = pl.DataFrame(
        {
            "dstream_data_id": pl.Series(
                "dstream_data_id",
                [0, 0, 1],
                dtype=pl.UInt64,
            ),
            "dstream_T": pl.Series(
                "dstream_T",
                [8, 8, 11],
                dtype=pl.UInt64,
            ),
            "dstream_value_bitwidth": pl.Series(
                "dstream_value_bitwidth",
                [
                    8,
                    8,
                    8,
                ],
                dtype=pl.UInt32,
            ),
            "dstream_value": pl.Series(
                "dstream_value",
                [7, 6, 6],
                dtype=pl.UInt64,
            ),
            "dstream_Tbar": pl.Series(
                "dstream_Tbar",
                [7, 6, 6],
                dtype=pl.UInt64,
            ),
        },
    ).select(
        pl.col(
            "dstream_data_id",
            "dstream_T",
            "dstream_Tbar",
            "dstream_value",
        )
        .sort_by("dstream_Tbar")
        .over(partition_by="dstream_data_id"),
    )
    res = build_tree_searchtable_cpp_from_exploded(
        exploded["dstream_data_id"].to_numpy(),
        exploded["dstream_T"].to_numpy(),
        exploded["dstream_Tbar"].to_numpy(),
        exploded["dstream_value"].to_numpy(),
        tqdm,
    )
    res = pl.DataFrame(res)
    assert alifestd_validate(
        alifestd_try_add_ancestor_list_col(res.to_pandas()),
    )
    assert alifestd_is_chronologically_ordered(
        alifestd_try_add_ancestor_list_col(
            res.with_columns(origin_time=pl.col("rank")).to_pandas(),
        ),
    )


# --- helpers for consolidation-with-dropped-differentia tests -----------


def _build(artifacts):
    """Convert [(data_id, T, ranks, diffs), ...] to tree dict via
    build_tree_searchtable_cpp_from_exploded."""
    all_data_ids = []
    all_Ts = []
    all_ranks = []
    all_diffs = []
    for data_id, T, art_ranks, art_diffs in artifacts:
        assert len(art_ranks) == len(art_diffs)
        for r, d in zip(art_ranks, art_diffs):
            all_data_ids.append(data_id)
            all_Ts.append(T)
            all_ranks.append(r)
            all_diffs.append(d)
    res = build_tree_searchtable_cpp_from_exploded(
        np.array(all_data_ids, dtype=np.uint64),
        np.array(all_Ts, dtype=np.uint64),
        np.array(all_ranks, dtype=np.uint64),
        np.array(all_diffs, dtype=np.uint64),
        tqdm,
    )
    # Convert to plain Python lists for easier debugging
    return {k: [int(x) for x in v] for k, v in res.items()}


def _dense(data_id, T, diffs):
    """Artifact retaining all ranks 0..len(diffs)-1."""
    return (data_id, T, list(range(len(diffs))), list(diffs))


def _sparse(data_id, T, rank_diff_pairs):
    """Artifact retaining only specified (rank, diff) pairs."""
    ranks = [r for r, d in rank_diff_pairs]
    diffs = [d for r, d in rank_diff_pairs]
    return (data_id, T, ranks, diffs)


def _mrca_rank(tree, id_a, id_b):
    """Find MRCA rank of two artifacts identified by dstream_data_id."""
    n = len(tree["id"])
    id_to_idx = {tree["id"][i]: i for i in range(n)}

    def find_leaf_id(data_id):
        for i in range(n):
            if tree["dstream_data_id"][i] == data_id:
                return tree["id"][i]
        raise ValueError(f"data_id {data_id} not found")

    def get_ancestor_chain(node_id):
        chain = []
        current = node_id
        while True:
            chain.append(current)
            idx = id_to_idx[current]
            parent = tree["ancestor_id"][idx]
            if parent == current:
                break
            current = parent
        return chain

    ancestors_a = set(get_ancestor_chain(find_leaf_id(id_a)))
    for nid in get_ancestor_chain(find_leaf_id(id_b)):
        if nid in ancestors_a:
            return tree["rank"][id_to_idx[nid]]

    raise RuntimeError("No common ancestor found")


# --- consolidation-with-dropped-differentia tests -----------------------


def test_single_dropped_rank():
    """Gap of 1 rank, match resumes.

    A (dense, T=8):   rank  0 1 2 3
                       diff  1 1 1 1
    B (sparse, T=12):  rank  0 _ 2 3
                       diff  1   1 1

    B drops rank 1; matches A at ranks 0, 2, 3.
    Expected MRCA(A,B) >= 3 (deep match despite gap).
    """
    tree = _build(
        [
            _dense(0, 8, [1, 1, 1, 1]),
            _sparse(1, 12, [(0, 1), (2, 1), (3, 1)]),
        ]
    )
    assert _mrca_rank(tree, 0, 1) >= 3


def test_three_consecutive_dropped_ranks():
    """Gap of 3, match resumes at rank 4.

    A (T=8):   rank  0 1 2 3 4
               diff  1 1 1 1 1
    B (T=16):  rank  0 _ _ _ 4
               diff  1       1

    B drops ranks 1-3; matches A at ranks 0 and 4.
    Expected MRCA(A,B) >= 4.
    """
    tree = _build(
        [
            _dense(0, 8, [1, 1, 1, 1, 1]),
            _sparse(1, 16, [(0, 1), (4, 1)]),
        ]
    )
    assert _mrca_rank(tree, 0, 1) >= 4


def test_gap_then_mismatch():
    """Gap of 3, differentia MISMATCH after gap -> diverge at rank 0.

    A (T=8):   rank  0 1 2 3 4
               diff  1 1 1 1 1
    B (T=16):  rank  0 _ _ _ 4
               diff  1       0

    B matches A at rank 0, drops 1-3, mismatches at rank 4.
    Expected MRCA(A,B) == 0 (last confirmed match before gap).
    """
    tree = _build(
        [
            _dense(0, 8, [1, 1, 1, 1, 1]),
            _sparse(1, 16, [(0, 1), (4, 0)]),
        ]
    )
    assert _mrca_rank(tree, 0, 1) == 0


def test_large_gap_only_endpoints():
    """Drop ranks 1-6, match at rank 7 only.

    A (T=8):   rank  0 1 2 3 4 5 6 7
               diff  1 1 1 1 1 1 1 1
    B (T=24):  rank  0 _ _ _ _ _ _ 7
               diff  1             1

    B retains only endpoints; matches A at ranks 0 and 7.
    Expected MRCA(A,B) >= 7.
    """
    tree = _build(
        [
            _dense(0, 8, [1, 1, 1, 1, 1, 1, 1, 1]),
            _sparse(1, 24, [(0, 1), (7, 1)]),
        ]
    )
    assert _mrca_rank(tree, 0, 1) >= 7


def test_two_separate_gaps():
    """Non-contiguous gaps with matches in between.

    A (T=8):   rank  0 1 2 3 4 5 6
               diff  1 0 1 1 0 1 1
    B (T=16):  rank  0 _ 2 3 _ 5 6
               diff  1   1 1   1 1

    B drops ranks 1 and 4; matches A at 0, 2, 3, 5, 6.
    Expected MRCA(A,B) >= 6.
    """
    tree = _build(
        [
            _dense(0, 8, [1, 0, 1, 1, 0, 1, 1]),
            _sparse(1, 16, [(0, 1), (2, 1), (3, 1), (5, 1), (6, 1)]),
        ]
    )
    assert _mrca_rank(tree, 0, 1) >= 6


def test_distractor_diverges_at_root():
    """Distractor lineage diverging at rank 0 + main + sparse newcomer.

    D (T=6):   rank  0 1 2      diff  0 1 1
    A (T=8):   rank  0 1 2 3    diff  1 1 1 1
    B (T=12):  rank  0 _ 2 3    diff  1   1 1

    D diverges from A at rank 0.  B matches A despite gap at rank 1.
    Expected: MRCA(A,B) >= 3, MRCA(D,A) == 0, MRCA(D,B) == 0.
    """
    tree = _build(
        [
            _dense(2, 6, [0, 1, 1]),
            _dense(0, 8, [1, 1, 1, 1]),
            _sparse(1, 12, [(0, 1), (2, 1), (3, 1)]),
        ]
    )
    assert _mrca_rank(tree, 0, 1) >= 3
    assert _mrca_rank(tree, 2, 0) == 0
    assert _mrca_rank(tree, 2, 1) == 0


def test_distractor_shares_prefix():
    """Distractor shares prefix then diverges + sparse newcomer.

    D (T=7):   rank  0 1 2      diff  1 1 0
    A (T=8):   rank  0 1 2 3    diff  1 1 1 1
    B (T=12):  rank  0 _ 2 3    diff  1   1 1

    D shares ranks 0,1 with A, diverges at rank 2.
    B skips rank 1, matches A at 2, 3.
    Expected: MRCA(A,B) >= 3, MRCA(D,A) >= 1.
    """
    tree = _build(
        [
            _dense(2, 7, [1, 1, 0]),
            _dense(0, 8, [1, 1, 1, 1]),
            _sparse(1, 12, [(0, 1), (2, 1), (3, 1)]),
        ]
    )
    assert _mrca_rank(tree, 0, 1) >= 3
    assert _mrca_rank(tree, 2, 0) >= 1


def test_two_main_items_then_sparse():
    """Two main lineage items (diverge late) + sparse newcomer.

    C (T=7):   rank  0 1 2 3 4    diff  1 1 1 0 1
    A (T=8):   rank  0 1 2 3 4    diff  1 1 1 1 1
    B (T=16):  rank  0 _ _ 3 4    diff  1     1 1

    C diverges from A at rank 3.  B skips 1-2, matches A at 3, 4.
    Expected: MRCA(A,B) >= 4, MRCA(A,C) >= 2.
    """
    tree = _build(
        [
            _dense(2, 7, [1, 1, 1, 0, 1]),
            _dense(0, 8, [1, 1, 1, 1, 1]),
            _sparse(1, 16, [(0, 1), (3, 1), (4, 1)]),
        ]
    )
    assert _mrca_rank(tree, 0, 1) >= 4
    assert _mrca_rank(tree, 0, 2) >= 2


def test_deep_tree_many_gaps():
    """T=32 main, T*=48 sparse with gaps every 4 ranks.

    A (T=32):  rank 0  1  2 ... 31   diff all 1
    B (T=48):  rank 0  _  _  _  4  _ ... 28  _ _ _ 31   diff all 1
               retained: {0, 4, 8, 12, 16, 20, 24, 28, 31}

    Expected MRCA(A,B) >= 28 (deep match despite many gaps).
    """
    a_diffs = [1] * 32
    b_ranks = [0, 4, 8, 12, 16, 20, 24, 28, 31]
    b_diffs = [1] * len(b_ranks)
    tree = _build(
        [
            _dense(0, 32, a_diffs),
            _sparse(1, 48, list(zip(b_ranks, b_diffs))),
        ]
    )
    assert _mrca_rank(tree, 0, 1) >= 28


def test_multiple_distractors_and_gaps():
    """Elaborate scenario with 4 artifacts and multiple divergence points.

    D1 (T=6):  rank  0 1 2          diff  0 1 1
    D2 (T=7):  rank  0 1 2 3        diff  1 1 0 1
    A  (T=8):  rank  0 1 2 3 4      diff  1 1 1 1 1
    B  (T=16): rank  0 _ 2 _ 4      diff  1   1   1

    D1 diverges from all at rank 0.
    D2 shares 0,1 with A, diverges at rank 2.
    B matches A at 0, skips 1, matches 2, skips 3, matches 4.
    Expected: MRCA(A,B) >= 4, MRCA(D1,A) == 0, MRCA(D2,A) >= 1.
    """
    tree = _build(
        [
            _dense(10, 6, [0, 1, 1]),
            _dense(11, 7, [1, 1, 0, 1]),
            _dense(0, 8, [1, 1, 1, 1, 1]),
            _sparse(1, 16, [(0, 1), (2, 1), (4, 1)]),
        ]
    )
    assert _mrca_rank(tree, 0, 1) >= 4
    assert _mrca_rank(tree, 10, 0) == 0
    assert _mrca_rank(tree, 11, 0) >= 1
    assert _mrca_rank(tree, 10, 1) == 0


def test_multi_clade_tree_with_cascading_sparsity():
    """Large-scale scenario: 6 dense reference lineages forming a binary
    tree with branching at ranks 0, 4, 8, 12, plus 5 sparse newcomers at
    varying sparsity levels that must navigate the tree correctly despite
    gaps - including gaps that span branching points.

    Tree topology (branching differentia in brackets):

        root -+- [r0=5]  clade L
              |    +- [r4=3]  clade LL
              |    |    +- [r8=7]  clade LLL
              |    |         +- [r12=2]  alpha    (100)
              |    |         +- [r12=9]  beta     (101)
              |    +- [r4=8]  gamma               (102)
              +- [r0=12] clade R
                   +- [r4=20] clade RL
                   |    +- [r8=25] delta          (103)
                   |    +- [r8=30] epsilon        (104)
                   +- [r4=35] zeta                (105)

    Non-branching ("filler") ranks all have differentia = 10.

    Sparse newcomers (all older, higher T -> inserted after dense):
      sparse_a  (200, T=48)  alpha lineage  retains {0,4,8,12,15}
      sparse_b  (201, T=48)  delta lineage  retains {0,4,8,14}
      sparse_c  (202, T=64)  beta lineage   retains {0,4,12,15} - skips r8
      sparse_d  (203, T=48)  RL lineage, diverges at r12 (diff=50)
                              retains {0,4,8,12} - all branch points present
      sparse_e  (204, T=48)  delta lineage  retains {0,8,14} - skips r4!
    """
    FILLER = 10

    # Branching differentia at key ranks; all other ranks get FILLER.
    branch_defs = {
        "alpha": {0: 5, 4: 3, 8: 7, 12: 2},
        "beta": {0: 5, 4: 3, 8: 7, 12: 9},
        "gamma": {0: 5, 4: 8, 8: 15},
        "delta": {0: 12, 4: 20, 8: 25},
        "epsilon": {0: 12, 4: 20, 8: 30},
        "zeta": {0: 12, 4: 35},
    }

    def make_diffs(branch, n=16):
        return [branch.get(r, FILLER) for r in range(n)]

    artifacts = [
        # --- 6 dense reference lineages (T=16, ranks 0-15) ---
        _dense(100, 16, make_diffs(branch_defs["alpha"])),
        _dense(101, 16, make_diffs(branch_defs["beta"])),
        _dense(102, 16, make_diffs(branch_defs["gamma"])),
        _dense(103, 16, make_diffs(branch_defs["delta"])),
        _dense(104, 16, make_diffs(branch_defs["epsilon"])),
        _dense(105, 16, make_diffs(branch_defs["zeta"])),
        # --- 5 sparse newcomers (higher T, fewer retained ranks) ---
        # sparse_a: alpha lineage, retains all branch points
        _sparse(
            200,
            48,
            [
                (0, 5),
                (4, 3),
                (8, 7),
                (12, 2),
                (15, FILLER),
            ],
        ),
        # sparse_b: delta lineage, retains all branch points
        _sparse(
            201,
            48,
            [
                (0, 12),
                (4, 20),
                (8, 25),
                (14, FILLER),
            ],
        ),
        # sparse_c: beta lineage, skips r8 (no branch in LL at r8)
        _sparse(
            202,
            64,
            [
                (0, 5),
                (4, 3),
                (12, 9),
                (15, FILLER),
            ],
        ),
        # sparse_d: RL lineage through r8=25, diverges at r12 with diff=50
        _sparse(
            203,
            48,
            [
                (0, 12),
                (4, 20),
                (8, 25),
                (12, 50),
            ],
        ),
        # sparse_e: delta lineage, skips r4 branching point!
        _sparse(
            204,
            48,
            [
                (0, 12),
                (8, 25),
                (14, FILLER),
            ],
        ),
    ]

    tree = _build(artifacts)

    # -- structural validation -----------------------------------------------
    res = pl.DataFrame(tree)
    assert alifestd_validate(
        alifestd_try_add_ancestor_list_col(res.to_pandas()),
    )
    assert alifestd_is_chronologically_ordered(
        alifestd_try_add_ancestor_list_col(
            res.with_columns(origin_time=pl.col("rank")).to_pandas(),
        ),
    )

    # Every artifact should appear as a leaf in the output tree.
    pv = int(placeholder_value)
    leaf_ids = {
        tree["dstream_data_id"][i]
        for i in range(len(tree["id"]))
        if tree["dstream_data_id"][i] != pv
    }
    expected_ids = {100, 101, 102, 103, 104, 105, 200, 201, 202, 203, 204}
    assert (
        expected_ids <= leaf_ids
    ), f"Missing leaves: {expected_ids - leaf_ids}"

    # -- Dense-to-dense reference MRCA checks --------------------------------
    # alpha vs beta: share LLL clade (through r8=7), diverge at r12.
    # After collapsing unifurcations r8->r11, MRCA rank >= 11.
    assert _mrca_rank(tree, 100, 101) >= 11

    # alpha vs gamma: share L clade, diverge at r4.
    # Collapsed chain r0->r3, MRCA rank >= 3.
    assert _mrca_rank(tree, 100, 102) >= 3

    # alpha vs delta: diverge at r0 (root).
    assert _mrca_rank(tree, 100, 103) == 0

    # gamma vs zeta: diverge at r0 (root).
    assert _mrca_rank(tree, 102, 105) == 0

    # delta vs epsilon: share RL clade (through r4=20), diverge at r8.
    # Collapsed chain r4->r7, MRCA rank >= 7.
    assert _mrca_rank(tree, 103, 104) >= 7

    # delta vs zeta: share R clade, diverge at r4.
    # Collapsed chain r0->r3 within R clade, MRCA rank >= 3.
    assert _mrca_rank(tree, 103, 105) >= 3

    # -- Sparse-to-dense: all branch points retained -----------------------
    # sparse_a tracks alpha, retains {0,4,8,12,15}: deep match.
    assert _mrca_rank(tree, 100, 200) >= 12

    # sparse_b tracks delta, retains {0,4,8,14}: deep match.
    assert _mrca_rank(tree, 103, 201) >= 8

    # -- Sparse-to-dense: gap skips non-branching rank ---------------------
    # sparse_c tracks beta, retains {0,4,12,15}: skips r8, but in the
    # LL clade there is no branch at r8 (alpha & beta both have 7 there).
    # Algorithm can traverse past r8 unambiguously.
    assert _mrca_rank(tree, 101, 202) >= 12

    # -- Sparse-to-dense: divergence after matching branch points ----------
    # sparse_d tracks delta lineage through r8=25, then diverges at
    # r12 (diff=50 vs filler=10).  Shares RL with delta through r8.
    assert _mrca_rank(tree, 103, 203) >= 8
    # sparse_d shares RL clade (r8) with epsilon but they diverge at r8
    # (delta r8=25, epsilon r8=30), so epsilon and sparse_d diverge earlier.
    assert _mrca_rank(tree, 104, 203) >= 7

    # -- Sparse-to-dense: gap spans a branching point ----------------------
    # sparse_e has ranks {0,8,14}, skipping r4 which is a branch point in
    # clade R (r4: 20->RL vs 35->zeta).  Algorithm must find r8=25 only in
    # the RL subtree and follow it.
    assert _mrca_rank(tree, 103, 204) >= 8
    # sparse_e should NOT be on zeta's branch (RR):
    assert _mrca_rank(tree, 105, 204) >= 3  # share R clade
    assert _mrca_rank(tree, 105, 204) < 8  # but not RL

    # -- Cross-clade checks --------------------------------------------------
    # alpha vs sparse_d: L vs R -> root.
    assert _mrca_rank(tree, 100, 203) == 0

    # gamma vs sparse_d: L vs R -> root.
    assert _mrca_rank(tree, 102, 203) == 0

    # zeta vs sparse_d: both R, diverge at r4.
    assert _mrca_rank(tree, 105, 203) >= 3

    # -- Sparse-to-sparse checks ---------------------------------------------
    # sparse_a (L) vs sparse_b (R): diverge at root.
    assert _mrca_rank(tree, 200, 201) == 0

    # sparse_a (alpha/L) vs sparse_c (beta/L): both in LLL, diverge at r12.
    assert _mrca_rank(tree, 200, 202) >= 8

    # sparse_d (RL) vs sparse_c (L): different clades -> root.
    assert _mrca_rank(tree, 203, 202) == 0

    # sparse_b (delta/RL) vs sparse_e (delta/RL): both track delta.
    assert _mrca_rank(tree, 201, 204) >= 8

    # sparse_d (RL-divergent) vs sparse_e (RL-delta): both in RL, share r8.
    assert _mrca_rank(tree, 203, 204) >= 8
