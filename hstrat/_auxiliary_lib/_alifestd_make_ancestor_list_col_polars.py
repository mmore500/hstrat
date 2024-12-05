import polars as pl


def alifestd_make_ancestor_list_col_polars(
    ids: pl.Series,
    ancestor_ids: pl.Series,
    root_ancestor_token: str = "none",
) -> pl.Series:
    """Translate a column of integer ancestor id values into alife standard
    `ancestor_list` representation.

    The option `root_ancestor_token` will be sandwiched in brackets to create
    the ancestor list entry for genesis organisms. For example, the token
    "None" will yield the entry "[None]" and the token "" will yield the entry
    "[]". Default "none".
    """

    res = ancestor_ids.cast(pl.String)
    res[ids == ancestor_ids] = root_ancestor_token
    return "[" + res + "]"
