from collections import Counter
import typing
import warnings

import numpy as np
import pandas as pd

from ._alifestd_assign_contiguous_ids import alifestd_assign_contiguous_ids
from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_asexual import alifestd_is_asexual
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_make_ancestor_list_col import alifestd_make_ancestor_list_col
from ._alifestd_parse_ancestor_ids import alifestd_parse_ancestor_ids
from ._alifestd_topological_sort import alifestd_topological_sort
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._jit import jit
from ._jit_numpy_int64_t import jit_numpy_int64_t


@jit(nopython=True)
def _collapse_unifurcations(
    ancestor_ids: np.array,
) -> typing.Tuple[np.array, np.array]:
    # assumes contiguous ids

    ref_counts = np.zeros(len(ancestor_ids), dtype=jit_numpy_int64_t)
    for ancestor_id in ancestor_ids:
        ref_counts[ancestor_id] += 1

    ids = np.arange(len(ancestor_ids))

    for pos in range(len(ancestor_ids)):

        ancestor_id = ancestor_ids[pos]
        id_ = ids[pos]
        assert id_ == pos
        assert ancestor_id <= id_
        ref_count = ref_counts[pos]

        if ref_count == 1 and id_ != ancestor_id:
            # percolate ancestor over self
            ancestor_ids[pos] = ancestor_ids[ancestor_id]
            ids[pos] = ids[ancestor_id]
        else:
            # update referenced ancestor
            ancestor_ids[pos] = ids[ancestor_id]

    keep_filter = ref_counts != 1 | (ancestor_ids == ids)

    return keep_filter, ancestor_ids


def _alifestd_collapse_unifurcations_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool,
) -> pd.DataFrame:
    """Optimized implementation for asexual phylogenies."""

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if not alifestd_is_topologically_sorted(phylogeny_df):
        phylogeny_df = alifestd_topological_sort(phylogeny_df, mutate=True)

    original_ids = phylogeny_df["id"].to_numpy().copy()
    if not alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df = alifestd_assign_contiguous_ids(
            phylogeny_df, mutate=True
        )

    keep_filter, ancestor_ids = _collapse_unifurcations(
        phylogeny_df["ancestor_id"].to_numpy()
    )
    phylogeny_df = phylogeny_df.loc[keep_filter]
    phylogeny_df.loc[:, "id"] = original_ids[keep_filter]
    phylogeny_df.loc[:, "ancestor_id"] = original_ids[
        ancestor_ids[keep_filter]
    ]
    phylogeny_df.loc[:, "ancestor_list"] = alifestd_make_ancestor_list_col(
        phylogeny_df["id"], phylogeny_df["ancestor_id"]
    )

    return phylogeny_df


def alifestd_collapse_unifurcations(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Pare record to bypass organisms with one ancestor and one descendant.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """

    if "branch_length" in phylogeny_df or "edge_length" in phylogeny_df:
        warnings.Warning(
            "alifestd_collapse_unifurcations does not update branch length "
            "columns. Use `origin_time` to recalculate branch lengths for "
            "collapsed phylogeny."
        )

    # special optimized handling for asexual phylogenies
    if alifestd_is_asexual(phylogeny_df):
        return _alifestd_collapse_unifurcations_asexual(
            phylogeny_df, mutate=mutate
        )

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if not alifestd_is_topologically_sorted(phylogeny_df):
        phylogeny_df = alifestd_topological_sort(phylogeny_df, mutate=True)

    phylogeny_df.set_index("id", drop=False, inplace=True)

    ref_counts = Counter(
        id_
        for ancestor_list_str in phylogeny_df["ancestor_list"]
        for id_ in alifestd_parse_ancestor_ids(ancestor_list_str)
    )

    for id_ in phylogeny_df["id"]:
        ancestor_ids = alifestd_parse_ancestor_ids(
            phylogeny_df.loc[id_, "ancestor_list"]
        )
        if len(ancestor_ids) == 1 and ref_counts[id_] == 1:
            # percolate ancestor over self
            (ancestor_id,) = ancestor_ids
            phylogeny_df.loc[id_] = phylogeny_df.loc[ancestor_id]
        elif len(ancestor_ids):
            # update referenced ancestor
            phylogeny_df.loc[id_, "ancestor_list"] = str(
                [
                    phylogeny_df.loc[ancestor_id, "id"]
                    for ancestor_id in ancestor_ids
                ]
            )

    assert "ancestor_id" not in phylogeny_df

    return phylogeny_df.drop_duplicates().reset_index(drop=True)
