import typing


def alifestd_parse_ancestor_ids(ancestor_list_str: str) -> typing.List[int]:
    if ancestor_list_str.lower() == "[none]":
        return []
    else:
        return eval(ancestor_list_str)
