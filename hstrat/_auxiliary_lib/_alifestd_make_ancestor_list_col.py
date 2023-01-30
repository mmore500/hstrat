import pandas as pd


def alifestd_make_ancestor_list_col(
    ids: pd.Series, ancestor_ids: pd.Series
) -> pd.Series:
    """TODO."""

    res = ancestor_ids.map("[{}]".format)
    res[ids == ancestor_ids] = "[none]"

    return res
