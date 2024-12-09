import re

from ...._auxiliary_lib import import_cpp_impls

_impl_mod = import_cpp_impls(
    "_build_tree_searchtable_cpp_impl",
    re.sub(r"\.[a-za-z0-9_]+$", "", __name__),
)
build_exploded, build_normal = _impl_mod.build_exploded, _impl_mod.build_normal
