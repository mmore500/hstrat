import pandas as pd


def alifestd_make_ancestor_id_col(
    ids: pd.Series, ancestor_lists: pd.Series
) -> pd.Series:
    """TODO."""
    ancestor_ids = (
        ancestor_lists.str.lower()
        .replace("[none]", "[-1]")
        .str.strip("[]")
        .astype(int)
    )

    root_filter = ancestor_ids == -1
    ancestor_ids[root_filter] = ids[root_filter]

    return ancestor_ids
