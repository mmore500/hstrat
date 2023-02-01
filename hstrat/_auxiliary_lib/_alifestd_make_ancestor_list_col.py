import pandas as pd


def alifestd_make_ancestor_list_col(
    ids: pd.Series, ancestor_ids: pd.Series
) -> pd.Series:
    """Translate a column of integer ancestor id values into alife standard
    `ancestor_list` representation."""

    res = ancestor_ids.map("[{}]".format)
    res[ids == ancestor_ids] = "[none]"

    return res
