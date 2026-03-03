import typing

from deprecated.sphinx import deprecated


@deprecated(
    version="1.23.0",
    reason="Use phyloframe.legacy.alifestd_parse_ancestor_id instead.",
)
def alifestd_parse_ancestor_id(ancestor_list_str: str) -> typing.Optional[int]:
    """Parse at most a single ancestor id from an `ancestor_list` field."""
    if ancestor_list_str.lower() in (
        "[]",
        "[none]",
    ):
        return None
    else:
        without_brackets_str = ancestor_list_str[1:-1]
        return int(without_brackets_str)
