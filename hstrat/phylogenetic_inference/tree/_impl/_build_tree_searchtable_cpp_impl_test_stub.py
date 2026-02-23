from ...._auxiliary_lib import get_package_name, load_cppimportable_module

_test_mod = load_cppimportable_module(
    "_build_tree_searchtable_cpp_impl_test", get_package_name(__name__)
)
