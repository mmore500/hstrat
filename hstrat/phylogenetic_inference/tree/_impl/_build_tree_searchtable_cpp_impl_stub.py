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
