import ast
import typing

from deprecated.sphinx import deprecated


@deprecated(
    version="1.23.0",
    reason="Use phyloframe.legacy.alifestd_parse_ancestor_ids instead.",
)
def alifestd_parse_ancestor_ids(ancestor_list_str: str) -> typing.List[int]:
    """Parse ancestor ids from an `ancestor_list` field."""
    if ancestor_list_str.lower() == "[none]":
        return []
    else:
        return ast.literal_eval(ancestor_list_str)
