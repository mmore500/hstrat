import re

from ...._auxiliary_lib import import_cpp_impls


build_exploded, build_normal = import_cpp_impls(
    "_build_tree_searchtable_cpp_impl",
    re.sub(r"\.[a-za-z0-9_]+$", "", __name__),
    ["build_exploded", "build_normal"],
)
