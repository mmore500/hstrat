import typing


def alifestd_parse_ancestor_ids(ancestor_list_str: str) -> typing.List[int]:
    """Parse ancestor ids from an `ancestor_list` field."""
    if ancestor_list_str.lower() == "[none]":
        return []
    else:
        return eval(ancestor_list_str)
