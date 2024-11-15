import pandas as pd


def alifestd_make_ancestor_list_col(
    ids: pd.Series, ancestor_ids: pd.Series, root_ancestor_token: str = "none"
) -> pd.Series:
    """Translate a column of integer ancestor id values into alife standard
    `ancestor_list` representation.

    The option `root_ancestor_token` will be sandwiched in brackets to create
    the ancestor list entry for genesis organisms. For example, the token
    "None" will yield the entry "[None]" and the token "" will yield the entry
    "[]". Default "none".
    """

    res = ancestor_ids.map("[{!s}]".format).astype(str)  # specify for empty
    res[ids == ancestor_ids] = f"[{root_ancestor_token}]"

    return res
