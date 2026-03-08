from ...._auxiliary_lib import get_package_name, load_cppimportable_module

_impl_mod = load_cppimportable_module(
    "_build_tree_searchtable_cpp_impl", get_package_name(__name__)
)
placeholder_value = _impl_mod.placeholder_value
Records = _impl_mod.Records
collapse_unifurcations = _impl_mod.collapse_unifurcations
copy_records_to_dict = _impl_mod.copy_records_to_dict
extract_records_to_dict = _impl_mod.extract_records_to_dict
extend_tree_searchtable_cpp_from_exploded = (
    _impl_mod.extend_tree_searchtable_cpp_from_exploded
)
build_tree_searchtable_cpp_from_exploded = (
    _impl_mod.build_tree_searchtable_cpp_from_exploded
)
build_tree_searchtable_cpp_from_nested = (
    _impl_mod.build_tree_searchtable_cpp_from_nested
)
check_trie_invariant_contiguous_ids = (
    _impl_mod.check_trie_invariant_contiguous_ids
)
check_trie_invariant_topologically_sorted = (
    _impl_mod.check_trie_invariant_topologically_sorted
)
check_trie_invariant_chronologically_sorted = (
    _impl_mod.check_trie_invariant_chronologically_sorted
)
check_trie_invariant_single_root = _impl_mod.check_trie_invariant_single_root
check_trie_invariant_search_children_valid = (
    _impl_mod.check_trie_invariant_search_children_valid
)
check_trie_invariant_search_children_sorted = (
    _impl_mod.check_trie_invariant_search_children_sorted
)
check_trie_invariant_no_indistinguishable_nodes = (
    _impl_mod.check_trie_invariant_no_indistinguishable_nodes
)
check_trie_invariant_data_nodes_are_leaves = (
    _impl_mod.check_trie_invariant_data_nodes_are_leaves
)
check_trie_invariant_search_lineage_compatible = (
    _impl_mod.check_trie_invariant_search_lineage_compatible
)
check_trie_invariant_ancestor_bounds = (
    _impl_mod.check_trie_invariant_ancestor_bounds
)
check_trie_invariant_root_at_zero = _impl_mod.check_trie_invariant_root_at_zero
check_trie_invariant_ranks_nonnegative = (
    _impl_mod.check_trie_invariant_ranks_nonnegative
)
describe_records = _impl_mod._describe_records
diagnose_trie_invariant_contiguous_ids = (
    _impl_mod.diagnose_trie_invariant_contiguous_ids
)
diagnose_trie_invariant_topologically_sorted = (
    _impl_mod.diagnose_trie_invariant_topologically_sorted
)
diagnose_trie_invariant_chronologically_sorted = (
    _impl_mod.diagnose_trie_invariant_chronologically_sorted
)
diagnose_trie_invariant_single_root = (
    _impl_mod.diagnose_trie_invariant_single_root
)
diagnose_trie_invariant_search_children_valid = (
    _impl_mod.diagnose_trie_invariant_search_children_valid
)
diagnose_trie_invariant_search_children_sorted = (
    _impl_mod.diagnose_trie_invariant_search_children_sorted
)
diagnose_trie_invariant_no_indistinguishable_nodes = (
    _impl_mod.diagnose_trie_invariant_no_indistinguishable_nodes
)
diagnose_trie_invariant_data_nodes_are_leaves = (
    _impl_mod.diagnose_trie_invariant_data_nodes_are_leaves
)
diagnose_trie_invariant_search_lineage_compatible = (
    _impl_mod.diagnose_trie_invariant_search_lineage_compatible
)
diagnose_trie_invariant_ancestor_bounds = (
    _impl_mod.diagnose_trie_invariant_ancestor_bounds
)
diagnose_trie_invariant_root_at_zero = (
    _impl_mod.diagnose_trie_invariant_root_at_zero
)
diagnose_trie_invariant_ranks_nonnegative = (
    _impl_mod.diagnose_trie_invariant_ranks_nonnegative
)
