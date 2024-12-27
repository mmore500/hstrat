from ...._auxiliary_lib import get_package_name, load_cppimportable_module

_impl_mod = load_cppimportable_module(
    "_build_tree_searchtable_cpp_impl", get_package_name(__name__)
)
records_to_dict = _impl_mod.records_to_dict
Records = _impl_mod.Records
extend_tree_searchtable_cpp_from_exploded = (
    _impl_mod.extend_tree_searchtable_cpp_from_exploded
)
build_tree_searchtable_cpp_from_exploded = (
    _impl_mod.build_tree_searchtable_cpp_from_exploded
)
build_tree_searchtable_cpp_from_nested = (
    _impl_mod.build_tree_searchtable_cpp_from_nested
)
