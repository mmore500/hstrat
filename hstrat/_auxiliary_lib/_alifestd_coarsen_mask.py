import typing
import warnings

import numpy as np
import pandas as pd

from ._alifestd_is_asexual import alifestd_is_asexual
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_make_ancestor_list_col import alifestd_make_ancestor_list_col
from ._alifestd_parse_ancestor_ids import alifestd_parse_ancestor_ids
from ._alifestd_topological_sort import alifestd_topological_sort
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def _alifestd_coarsen_mask_asexual(
    phylogeny_df: pd.DataFrame,
    mask: pd.Series,  # boolean mask
    progress_wrap: typing.Callable,
) -> pd.DataFrame:

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if not alifestd_is_topologically_sorted(phylogeny_df):
        phylogeny_df = alifestd_topological_sort(phylogeny_df, mutate=True)

    root_token_str = phylogeny_df["ancestor_list"].iat[0]
    assert root_token_str[0] == "[" and root_token_str[-1] == "]"
    assert not any(c.isdigit() for c in root_token_str)

    phylogeny_df.set_index("id", drop=False, inplace=True)

    coarsened_ids = {*phylogeny_df.loc[mask, "id"]}
    new_ancestor_ids = {}  # int id --> int ancestor_id
    for idx in progress_wrap(phylogeny_df.index):
        ancestor_id = phylogeny_df.at[idx, "ancestor_id"]

        if ancestor_id in coarsened_ids:
            new_ancestor_ids[idx] = ancestor_id
        elif ancestor_id in new_ancestor_ids:
            assert ancestor_id != idx
            ancestor_id = new_ancestor_ids[ancestor_id]
            new_ancestor_ids[idx] = ancestor_id

    res = phylogeny_df[mask].reset_index(drop=True)
    res["ancestor_id"] = (
        # non-exhaustive mapping,
        # see https://stackoverflow.com/a/41678874/17332200
        res["id"]
        .map(new_ancestor_ids)
        .fillna(res["id"])
        .astype(int)
    )

    res["ancestor_list"] = alifestd_make_ancestor_list_col(
        res["id"], res["ancestor_id"], root_token_str[1:-1]
    )

    return res


def _alifestd_coarsen_mask_sexual(
    phylogeny_df: pd.DataFrame,
    mask: pd.Series,  # boolean mask
    progress_wrap: typing.Callable,
) -> pd.DataFrame:

    if not alifestd_is_topologically_sorted(phylogeny_df):
        phylogeny_df = alifestd_topological_sort(phylogeny_df, mutate=True)

    root_token_str = phylogeny_df["ancestor_list"].iat[0]
    assert not any(c.isdigit() for c in root_token_str)

    phylogeny_df.set_index("id", drop=False, inplace=True)

    coarsened_ids = {*phylogeny_df.loc[mask, "id"]}
    new_ancestor_lists = {}  # int id --> list[int] ancestor_ids
    for idx in progress_wrap(phylogeny_df.index):
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
        res["id"]
        .map(new_ancestor_lists)
        .apply(np.unique)  # sort and prevent duplicate values
        .apply(np.ndarray.tolist)
        .apply(str)
        .replace("[]", root_token_str)
    )

    # don't need update because not in sexual phylos
    assert "ancestor_id" not in phylogeny_df

    return res


def alifestd_coarsen_mask(
    phylogeny_df: pd.DataFrame,
    mask: pd.Series,  # boolean mask
    mutate: bool = False,
    progress_wrap: typing.Callable = lambda x: x,
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

    if len(phylogeny_df) <= 1:
        return phylogeny_df

    if alifestd_is_asexual(phylogeny_df):
        return _alifestd_coarsen_mask_asexual(
            phylogeny_df, mask, progress_wrap
        )
    else:
        return _alifestd_coarsen_mask_sexual(phylogeny_df, mask, progress_wrap)
