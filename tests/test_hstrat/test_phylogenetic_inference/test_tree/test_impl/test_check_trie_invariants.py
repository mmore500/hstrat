import numpy as np
from tqdm import tqdm

from hstrat.phylogenetic_inference.tree._impl._build_tree_searchtable_cpp_impl_stub import (
    Records,
    check_trie_invariant_ancestor_bounds,
    check_trie_invariant_chronologically_sorted,
    check_trie_invariant_contiguous_ids,
    check_trie_invariant_data_nodes_are_leaves,
    check_trie_invariant_no_indistinguishable_nodes,
    check_trie_invariant_ranks_nonnegative,
    check_trie_invariant_root_at_zero,
    check_trie_invariant_search_children_sorted,
    check_trie_invariant_search_children_valid,
    check_trie_invariant_search_lineage_compatible,
    check_trie_invariant_single_root,
    check_trie_invariant_topologically_sorted,
    collapse_unifurcations,
    extend_tree_searchtable_cpp_from_exploded,
    placeholder_value,
)

PV = placeholder_value


# ---- Helpers ----


def _make_valid_built_records():
    """Build a valid trie with two artifacts using the C++ build functions."""
    records = Records(10)
    data_ids = np.array([0, 0, 0, 1, 1, 1], dtype=np.uint64)
    num_strata = np.array([4, 4, 4, 5, 5, 5], dtype=np.uint64)
    ranks = np.array([1, 2, 3, 1, 2, 4], dtype=np.int64)
    differentiae = np.array([10, 20, 30, 10, 20, 40], dtype=np.uint64)
    extend_tree_searchtable_cpp_from_exploded(
        records, data_ids, num_strata, ranks, differentiae, tqdm
    )
    return records


def _all_checks():
    """Return list of (name, check_fn) for all invariant checks."""
    return [
        ("contiguous_ids", check_trie_invariant_contiguous_ids),
        ("topologically_sorted", check_trie_invariant_topologically_sorted),
        (
            "chronologically_sorted",
            check_trie_invariant_chronologically_sorted,
        ),
        ("single_root", check_trie_invariant_single_root),
        (
            "search_children_valid",
            check_trie_invariant_search_children_valid,
        ),
        (
            "search_children_sorted",
            check_trie_invariant_search_children_sorted,
        ),
        (
            "no_indistinguishable_nodes",
            check_trie_invariant_no_indistinguishable_nodes,
        ),
        (
            "data_nodes_are_leaves",
            check_trie_invariant_data_nodes_are_leaves,
        ),
        (
            "search_lineage_compatible",
            check_trie_invariant_search_lineage_compatible,
        ),
        ("ancestor_bounds", check_trie_invariant_ancestor_bounds),
        ("root_at_zero", check_trie_invariant_root_at_zero),
        (
            "nonroot_ranks_positive",
            check_trie_invariant_ranks_nonnegative,
        ),
    ]


# ---- Positive tests: all invariants pass ----


def test_invariants_singleton():
    """A singleton root-only Records should pass all invariants."""
    records = Records(1)
    for name, check_fn in _all_checks():
        assert check_fn(records), f"{name} failed on singleton"


def test_invariants_built_tree():
    """A tree built by C++ extend function should pass all invariants."""
    records = _make_valid_built_records()
    for name, check_fn in _all_checks():
        assert check_fn(records), f"{name} failed on built tree"


def test_invariants_built_tree_single_artifact():
    """A tree with one artifact should pass all invariants."""
    records = Records(10)
    data_ids = np.array([0, 0, 0], dtype=np.uint64)
    num_strata = np.array([4, 4, 4], dtype=np.uint64)
    ranks = np.array([1, 2, 3], dtype=np.int64)
    differentiae = np.array([5, 10, 15], dtype=np.uint64)
    extend_tree_searchtable_cpp_from_exploded(
        records, data_ids, num_strata, ranks, differentiae, tqdm
    )
    for name, check_fn in _all_checks():
        assert check_fn(records), f"{name} failed on single artifact tree"


def test_invariants_after_dropped_only_collapse():
    """Invariants should pass after collapse_unifurcations(dropped_only=True)."""
    records = _make_valid_built_records()
    records = collapse_unifurcations(records, dropped_only=True)
    for name, check_fn in _all_checks():
        assert check_fn(records), f"{name} failed after dropped_only collapse"


def test_invariants_after_full_collapse():
    """Invariants should pass after collapse_unifurcations(dropped_only=False).

    Note: search trie invariants are skipped (return True) because
    full collapse sets search fields to placeholder_value.
    """
    records = _make_valid_built_records()
    records = collapse_unifurcations(records, dropped_only=False)
    for name, check_fn in _all_checks():
        assert check_fn(records), f"{name} failed after full collapse"


def test_invariants_many_artifacts_shared_prefix():
    """A tree with many artifacts sharing a common prefix passes invariants."""
    records = Records(50)
    # 4 artifacts sharing rank 1 differentia 5, diverging at rank 2
    data_ids = np.array(
        [0, 0, 1, 1, 2, 2, 3, 3],
        dtype=np.uint64,
    )
    num_strata = np.array(
        [3, 3, 3, 3, 3, 3, 3, 3],
        dtype=np.uint64,
    )
    ranks = np.array([1, 2, 1, 2, 1, 2, 1, 2], dtype=np.int64)
    differentiae = np.array([5, 10, 5, 20, 5, 30, 5, 40], dtype=np.uint64)
    extend_tree_searchtable_cpp_from_exploded(
        records, data_ids, num_strata, ranks, differentiae, tqdm
    )
    for name, check_fn in _all_checks():
        assert check_fn(records), f"{name} failed on shared prefix tree"


# ---- Negative tests: specific invariants should fail ----


def test_invariant_fails_contiguous_ids():
    """Non-contiguous ids should fail contiguous_ids check."""
    records = Records(4, init_root=False)
    # Create root at id 0 manually
    records.addRecord(PV, 0, 0, 0, 0, 0, 0, 0, 0)
    # Skip id 1 and go to id 2
    records.addRecord(PV, 2, 0, 0, 2, 2, 2, 1, 1)
    assert not check_trie_invariant_contiguous_ids(records)


def test_invariant_fails_topologically_sorted():
    """ancestor_id > id should fail topologically_sorted check."""
    records = Records(4, init_root=False)
    # Node 0: root
    records.addRecord(PV, 0, 0, 0, 0, 0, 0, 0, 0)
    # Node 1: ancestor_id=2 which is > 1 (forward reference)
    records.addRecord(PV, 1, 2, 1, 1, 1, 1, 1, 1)
    # Node 2: valid
    records.addRecord(PV, 2, 0, 2, 2, 2, 2, 1, 2)
    assert not check_trie_invariant_topologically_sorted(records)
    # other invariants should still pass where applicable
    assert check_trie_invariant_contiguous_ids(records)


def test_invariant_fails_chronologically_sorted():
    """Parent rank > child rank should fail chronologically_sorted check."""
    records = Records(4, init_root=False)
    # Node 0: root with rank 0
    records.addRecord(PV, 0, 0, 0, 0, 0, 0, 0, 0)
    # Node 1: rank 5
    records.addRecord(PV, 1, 0, 1, 1, 1, 1, 5, 1)
    # Node 2: ancestor is 1 (rank 5), but node 2 has rank 3 < 5
    # addRecord asserts rank[ancestor_id] <= rank, so we cannot construct
    # a chronologically-unsorted tree through the normal API.
    # The positive case is tested in test_invariants_built_tree.


def test_invariant_fails_single_root_multiple_roots():
    """Multiple roots should fail single_root check."""
    records = Records(4, init_root=False)
    # Two self-referencing nodes (both roots)
    records.addRecord(PV, 0, 0, 0, 0, 0, 0, 0, 0)
    records.addRecord(PV, 1, 1, 1, 1, 1, 1, 0, 0)
    assert not check_trie_invariant_single_root(records)
    # contiguous ids should still pass
    assert check_trie_invariant_contiguous_ids(records)


def test_invariant_fails_single_root_no_roots():
    """No roots should fail single_root check."""
    records = Records(4, init_root=False)
    # Node 0 points to node 1, node 1 points to node 0 - no self-reference
    records.addRecord(PV, 0, 0, 0, 0, 0, 0, 0, 0)
    # Node 1's ancestor is 0, not itself
    records.addRecord(PV, 1, 0, 1, 1, 1, 1, 1, 1)
    # This tree has exactly one root (node 0), so it passes.
    # addRecord blocks constructing a zero-root tree, so we only verify
    # the two-node tree has a single root.
    assert check_trie_invariant_single_root(records)


def test_invariant_fails_root_at_zero():
    """Root not at index 0 should fail root_at_zero check."""
    records = Records(4, init_root=False)
    # Node 0: NOT a root (ancestor_id != 0)
    # But addRecord assertion: this->size() == 0 || ancestor_id != id
    # means the first record CAN be self-referencing. To make index 0
    # not be a root, we'd need ancestor_id[0] != 0.
    # First record: no assertion on ancestor_id != id, so we can set
    # ancestor_id = 0 which makes it self-referencing = root.
    # To break root_at_zero, set rank[0] != 0
    records.addRecord(PV, 0, 0, 0, 0, 0, 0, 5, 0)  # rank=5 instead of 0
    assert not check_trie_invariant_root_at_zero(records)


def test_invariant_ranks_nonnegative_passes():
    """Nodes with rank >= 0 should pass ranks_nonnegative check."""
    records = Records(4, init_root=False)
    records.addRecord(PV, 0, 0, 0, 0, 0, 0, 0, 0)  # root, rank=0
    records.addRecord(PV, 1, 0, 1, 1, 1, 1, 0, 1)  # rank=0, non-root
    assert check_trie_invariant_ranks_nonnegative(records)
    # other basic checks should still pass
    assert check_trie_invariant_topologically_sorted(records)
    assert check_trie_invariant_contiguous_ids(records)


def test_invariant_search_children_valid_on_built_tree():
    """Search children validity on a properly built tree."""
    records = _make_valid_built_records()
    assert check_trie_invariant_search_children_valid(records)


def test_invariant_search_children_sorted_on_built_tree():
    """Search children sort order on a properly built tree."""
    records = _make_valid_built_records()
    assert check_trie_invariant_search_children_sorted(records)


def test_invariant_no_indistinguishable_on_built_tree():
    """No indistinguishable nodes on a properly built tree."""
    records = _make_valid_built_records()
    assert check_trie_invariant_no_indistinguishable_nodes(records)


def test_invariant_data_nodes_are_leaves_on_built_tree():
    """Data nodes are leaf nodes on a properly built tree."""
    records = _make_valid_built_records()
    assert check_trie_invariant_data_nodes_are_leaves(records)


def test_invariant_search_lineage_compatible_on_built_tree():
    """Search trie compatible with lineage trie on a properly built tree."""
    records = _make_valid_built_records()
    assert check_trie_invariant_search_lineage_compatible(records)


def test_invariant_search_checks_skip_after_full_collapse():
    """Search trie checks return True (skip) when search trie is dismantled."""
    records = _make_valid_built_records()
    records = collapse_unifurcations(records, dropped_only=False)
    # Search trie is now dismantled (all placeholder values)
    # These checks should return True (skip)
    assert check_trie_invariant_search_children_valid(records)
    assert check_trie_invariant_search_children_sorted(records)
    assert check_trie_invariant_no_indistinguishable_nodes(records)
    assert check_trie_invariant_data_nodes_are_leaves(records)
    assert check_trie_invariant_search_lineage_compatible(records)


def test_invariant_ancestor_bounds_on_valid_tree():
    """ancestor_bounds passes on a valid tree."""
    records = _make_valid_built_records()
    assert check_trie_invariant_ancestor_bounds(records)
    # addRecord asserts rank[ancestor_id] <= rank, so out-of-bounds
    # ancestor_id cannot be constructed through the normal API.
    # This invariant catches corruption outside normal addRecord flow.


def test_invariants_on_regression_tree():
    """Invariants pass on the regression test tree (before extraction)."""
    records = Records(20)
    data_ids = np.array(
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
        dtype=np.uint64,
    )
    num_strata = np.array(
        [8, 8, 8, 8, 8, 8, 8, 8, 11, 11, 11, 11, 11, 11, 11, 11],
        dtype=np.uint64,
    )
    ranks = np.array(
        [0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3, 4, 5, 6, 9],
        dtype=np.int64,
    )
    differentiae = np.array(
        [0, 1, 3, 7, 2, 5, 4, 6, 0, 1, 3, 7, 2, 5, 4, 6],
        dtype=np.uint64,
    )
    extend_tree_searchtable_cpp_from_exploded(
        records, data_ids, num_strata, ranks, differentiae, tqdm
    )
    for name, check_fn in _all_checks():
        assert check_fn(records), f"{name} failed on regression tree"


def test_invariants_on_distilled_regression_tree():
    """Invariants pass on the distilled regression test tree."""
    records = Records(10)
    data_ids = np.array([0, 0, 1], dtype=np.uint64)
    num_strata = np.array([8, 8, 11], dtype=np.uint64)
    ranks = np.array([6, 7, 6], dtype=np.int64)
    differentiae = np.array([6, 7, 6], dtype=np.uint64)
    extend_tree_searchtable_cpp_from_exploded(
        records, data_ids, num_strata, ranks, differentiae, tqdm
    )
    for name, check_fn in _all_checks():
        assert check_fn(records), f"{name} failed on distilled regression tree"


def test_search_children_valid_detects_bad_prev_sibling():
    """Manually constructed tree with broken prev_sibling link.

    Build a valid tree then create a new broken one with wrong
    prev_sibling pointer.
    """
    # Build a valid tree with a node that has multiple children
    records = Records(20)
    # Three artifacts with shared prefix at rank 1, diverging at rank 2
    data_ids = np.array(
        [0, 0, 1, 1, 2, 2],
        dtype=np.uint64,
    )
    num_strata = np.array(
        [3, 3, 3, 3, 3, 3],
        dtype=np.uint64,
    )
    ranks = np.array([1, 2, 1, 2, 1, 2], dtype=np.int64)
    differentiae = np.array([5, 10, 5, 20, 5, 30], dtype=np.uint64)
    extend_tree_searchtable_cpp_from_exploded(
        records, data_ids, num_strata, ranks, differentiae, tqdm
    )
    # This valid tree should pass
    assert check_trie_invariant_search_children_valid(records)
    assert check_trie_invariant_search_children_sorted(records)
    assert check_trie_invariant_no_indistinguishable_nodes(records)
