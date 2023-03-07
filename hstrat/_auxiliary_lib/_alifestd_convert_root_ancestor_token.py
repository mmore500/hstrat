import pandas as pd


def alifestd_convert_root_ancestor_token(
    ancestor_list: pd.Series,
    root_ancestor_token: str,
    mutate: bool = False,
) -> pd.Series:
    """Set `root_ancestor_token` for ancestor_list series.

    The option `root_ancestor_token` will be sandwiched in brackets to create
    the ancestor list entry for genesis organisms. For example, the token
    "None" will yield the entry "[None]" and the token "" will yield the entry
    """

    if not mutate:
        ancestor_list = ancestor_list.copy()

    ancestor_list[
        ancestor_list.str.lower().isin(("[none]", "[]"))
    ] = f"[{root_ancestor_token}]"
    return ancestor_list
