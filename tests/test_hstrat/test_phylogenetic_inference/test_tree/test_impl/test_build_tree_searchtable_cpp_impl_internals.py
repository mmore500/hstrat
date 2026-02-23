"""
Thin pytest wrappers around the C++ unit tests in
_build_tree_searchtable_cpp_impl_test.cpp.

Each test_* function calls the corresponding C++ function exported via
pybind11.  On failure the C++ side throws std::runtime_error (with a message
identifying file and line), which pybind11 converts to RuntimeError here.
No new dependencies are required beyond what is already used by the project.
"""

import pytest

from hstrat.phylogenetic_inference.tree._impl._build_tree_searchtable_cpp_impl_test_stub import (
    _test_mod as _cpp,
)


# ---------------------------------------------------------------------------
# Records
# ---------------------------------------------------------------------------


def test_records_root_state():
    _cpp.test_records_root_state()


def test_records_add_child():
    _cpp.test_records_add_child()


def test_records_max_differentia_tracked():
    _cpp.test_records_max_differentia_tracked()


# ---------------------------------------------------------------------------
# attach_search_parent / detach_search_parent
# ---------------------------------------------------------------------------


def test_attach_single_child():
    _cpp.test_attach_single_child()


def test_attach_two_children_rank_order():
    _cpp.test_attach_two_children_rank_order()


def test_attach_insert_middle():
    _cpp.test_attach_insert_middle()


def test_detach_sole_child():
    _cpp.test_detach_sole_child()


def test_detach_first_of_two():
    _cpp.test_detach_first_of_two()


def test_detach_last_of_three():
    _cpp.test_detach_last_of_three()


def test_detach_middle_of_three():
    _cpp.test_detach_middle_of_three()


def test_attach_after_detach():
    _cpp.test_attach_after_detach()


# ---------------------------------------------------------------------------
# consolidate_trie
# ---------------------------------------------------------------------------


def test_consolidate_no_children():
    _cpp.test_consolidate_no_children()


def test_consolidate_children_already_at_rank():
    _cpp.test_consolidate_children_already_at_rank()


def test_consolidate_promotes_grandchild_to_rank():
    _cpp.test_consolidate_promotes_grandchild_to_rank()


def test_consolidate_two_levels_deep():
    _cpp.test_consolidate_two_levels_deep()


def test_consolidate_multiple_grandchildren():
    _cpp.test_consolidate_multiple_grandchildren()


def test_consolidate_merges_indistinguishable_grandchildren():
    _cpp.test_consolidate_merges_indistinguishable_grandchildren()


# ---------------------------------------------------------------------------
# collapse_indistinguishable_nodes
# ---------------------------------------------------------------------------


def test_collapse_no_duplicates_unchanged():
    _cpp.test_collapse_no_duplicates_unchanged()


def test_collapse_two_identical_children():
    _cpp.test_collapse_two_identical_children()


def test_collapse_loser_children_reparented():
    _cpp.test_collapse_loser_children_reparented()


# ---------------------------------------------------------------------------
# place_allele
# ---------------------------------------------------------------------------


def test_place_allele_creates_new_node():
    _cpp.test_place_allele_creates_new_node()


def test_place_allele_finds_existing_match():
    _cpp.test_place_allele_finds_existing_match()


def test_place_allele_different_diff_creates_new():
    _cpp.test_place_allele_different_diff_creates_new()


def test_place_allele_different_rank_creates_new():
    _cpp.test_place_allele_different_rank_creates_new()


# ---------------------------------------------------------------------------
# create_offstring
# ---------------------------------------------------------------------------


def test_create_offstring_stores_data_id():
    _cpp.test_create_offstring_stores_data_id()


def test_create_offstring_attaches_to_parent():
    _cpp.test_create_offstring_attaches_to_parent()


def test_create_offstring_sequential_ids():
    _cpp.test_create_offstring_sequential_ids()


# ---------------------------------------------------------------------------
# insert_artifact
# ---------------------------------------------------------------------------


def test_insert_artifact_single_rank():
    _cpp.test_insert_artifact_single_rank()


def test_insert_artifact_builds_path():
    _cpp.test_insert_artifact_builds_path()


def test_insert_artifact_shared_prefix():
    _cpp.test_insert_artifact_shared_prefix()


def test_insert_artifact_gap_consolidates():
    _cpp.test_insert_artifact_gap_consolidates()
