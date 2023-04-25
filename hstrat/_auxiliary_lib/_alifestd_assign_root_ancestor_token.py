import pandas as pd

from ._alifestd_convert_root_ancestor_token import (
    alifestd_convert_root_ancestor_token,
)


def alifestd_assign_root_ancestor_token(
    phylogeny_df: pd.DataFrame,
    root_ancestor_token: str,
    mutate: bool = False,
) -> pd.DataFrame:
    """Set `root_ancestor_token` for "ancestor_list" column.

    The option `root_ancestor_token` will be sandwiched in brackets to create
    the ancestor list entry for genesis organisms. For example, the token
    "None" will yield the entry "[None]" and the token "" will yield the entry
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df["ancestor_list"] = alifestd_convert_root_ancestor_token(
        phylogeny_df["ancestor_list"],
        root_ancestor_token,
        mutate=False,  # prevent assign to slice warning
    )

    return phylogeny_df
