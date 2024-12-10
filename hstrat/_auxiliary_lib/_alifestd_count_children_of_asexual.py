import pandas as pd

from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def alifestd_count_children_of_asexual(
    phylogeny_df: pd.DataFrame,
    parent: int,
    mutate: bool = False,
) -> int:
    """How many taxa are direct descendants of the given parent?

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if not (phylogeny_df["id"] == parent).any():
        raise ValueError(f"Parent {parent} not found in phylogeny dataframe.")

    is_root = phylogeny_df["ancestor_id"] == phylogeny_df["id"]
    return ((phylogeny_df["ancestor_id"] == parent) & ~is_root).sum()
