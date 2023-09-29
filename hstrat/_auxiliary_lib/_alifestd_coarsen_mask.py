import warnings

import pandas as pd

from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_make_ancestor_id_col import alifestd_make_ancestor_id_col
from ._alifestd_parse_ancestor_ids import alifestd_parse_ancestor_ids
from ._alifestd_topological_sort import alifestd_topological_sort


def alifestd_coarsen_mask(
    phylogeny_df: pd.DataFrame,
    mask: pd.Series,  # boolean mask
    mutate: bool = False,
) -> pd.DataFrame:
    """Pare record to bypass organisms outside mask.

    The root ancestor token will be adopted from phylogeny_df.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """

    if "branch_length" in phylogeny_df or "edge_length" in phylogeny_df:
        warnings.warn(
            "alifestd_coarsen_mask does not update branch length columns. "
            "Use `origin_time` to recalculate branch lengths for coarsened "
            "phylogeny."
        )

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if not alifestd_is_topologically_sorted(phylogeny_df):
        phylogeny_df = alifestd_topological_sort(phylogeny_df, mutate=True)

    root_token_str = phylogeny_df["ancestor_list"].iat[0]
    assert not any(c.isdigit() for c in root_token_str)

    phylogeny_df.set_index("id", drop=False, inplace=True)

    coarsened_ids = {*phylogeny_df.loc[mask, "id"]}
    new_ancestor_lists = {}  # int id --> list[int] ancestor_ids
    for idx in phylogeny_df.index:
        ancestor_list = phylogeny_df.at[idx, "ancestor_list"]
        ancestor_ids = alifestd_parse_ancestor_ids(ancestor_list)

        new_ancestor_ids = []
        for ancestor_id in ancestor_ids:
            if ancestor_id in coarsened_ids:
                new_ancestor_ids.append(ancestor_id)
            else:
                new_ancestor_ids.extend(new_ancestor_lists[ancestor_id])

        new_ancestor_lists[idx] = new_ancestor_ids

    res = phylogeny_df[mask].reset_index(drop=True)
    res["ancestor_list"] = (
        res["id"].map(new_ancestor_lists).apply(str).replace("[]", "[none]")
    )

    if "ancestor_id" in phylogeny_df:
        res["ancestor_id"] = alifestd_make_ancestor_id_col(
            res["id"], res["ancestor_list"]
        )
    return res
