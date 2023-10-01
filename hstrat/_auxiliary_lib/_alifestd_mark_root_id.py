import typing

import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_parse_ancestor_ids import alifestd_parse_ancestor_ids
from ._alifestd_topological_sort import alifestd_topological_sort
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def alifestd_mark_root_id(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
    selector: typing.Callable = min,
) -> pd.DataFrame:
    """Add column `root_id`, containing the `id` of entries' ultimate ancestor.

    For sexual data, the field `root_id` is chosen according to the selection
    of callable `selector` over parents' `root_id` values. Note that subsets
    within a connected component may be marked with different `root_id` values.
    To create a component id that is consistent within connected components,
    a backward pass could be performed that updates ancestors' values if they
    are greater than that of each descendant.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if not alifestd_is_topologically_sorted(phylogeny_df):
        phylogeny_df = alifestd_topological_sort(phylogeny_df, mutate=True)

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.index = phylogeny_df["id"]

    phylogeny_df["root_id"] = phylogeny_df["id"]
    if "ancestor_id" in phylogeny_df.columns:  # asexual
        root_id_col = phylogeny_df["root_id"]
        ancestor_id_col = phylogeny_df["ancestor_id"]
        for index in phylogeny_df.index:
            ancestor_id = ancestor_id_col.at[index]
            root_id_col.at[index] = root_id_col.at[ancestor_id]
    else:  # sexual
        root_id_col = phylogeny_df["root_id"]
        ancestor_list_col = phylogeny_df["ancestor_list"]
        for index in phylogeny_df.index:
            ancestor_list = ancestor_list_col.at[index]
            ancestor_ids = alifestd_parse_ancestor_ids(ancestor_list)
            candidate_roots = [*map(root_id_col.at.__getitem__, ancestor_ids)]
            # "or" covers genesis empty list case
            root_id_col.at[index] = selector(candidate_roots or [index])

    return phylogeny_df
