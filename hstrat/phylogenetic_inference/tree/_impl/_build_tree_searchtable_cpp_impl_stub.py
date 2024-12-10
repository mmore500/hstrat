from ...._auxiliary_lib import delegate_cppimport_module, get_package_name

_impl_mod = delegate_cppimport_module(
    "_build_tree_searchtable_cpp_impl", get_package_name(__name__)
)
build_tree_searchtable_cpp_from_exploded = (
    _impl_mod.build_tree_searchtable_cpp_from_exploded
)
build_tree_searchtable_cpp_from_nested = (
    _impl_mod.build_tree_searchtable_cpp_from_nested
)
