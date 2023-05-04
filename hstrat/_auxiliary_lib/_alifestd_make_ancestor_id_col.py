import pandas as pd


def alifestd_make_ancestor_id_col(
    ids: pd.Series, ancestor_lists: pd.Series
) -> pd.Series:
    """Translate ancestor ids from a column of singleton `ancestor_list`s into a
    pure-integer series representation.

    Each organism must have one or zero ancestors (i.e., asexualasexual data).
    In the returned series, ancestor id will be assigned to own id for no-
    ancestor organisms.
    """
    ancestor_ids = (
        ancestor_lists.astype("str")
        .str.lower()
        .replace("[none]", "[-1]")
        .replace("[]", "[-1]")
        .str.strip("[]")
        .astype(int)
    )

    root_filter = ancestor_ids == -1
    ancestor_ids[root_filter] = ids[root_filter]

    return ancestor_ids
