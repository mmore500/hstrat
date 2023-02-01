from collections import Counter
import typing
import warnings

import numpy as np
import pandas as pd

from ._alifestd_assign_contiguous_ids import alifestd_assign_contiguous_ids
from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_asexual import alifestd_is_asexual
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_make_ancestor_id_col import alifestd_make_ancestor_id_col
from ._alifestd_make_ancestor_list_col import alifestd_make_ancestor_list_col
from ._alifestd_parse_ancestor_ids import alifestd_parse_ancestor_ids
from ._alifestd_to_working_format import alifestd_to_working_format
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
        id = ids[pos]
        assert id == pos
        assert ancestor_id <= id
        ref_count = ref_counts[pos]

        if ref_count == 1 and id != ancestor_id:
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
) -> pd.DataFrame:
    """Optimized implementation for asexual phylogenies."""

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df)

    if not alifestd_is_topologically_sorted(phylogeny_df):
        phylogeny_df = alifestd_topological_sort(phylogeny_df)

    original_ids = phylogeny_df["id"].to_numpy()
    if not alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df = alifestd_assign_contiguous_ids(phylogeny_df)

    keep_filter, ancestor_ids = _collapse_unifurcations(
        # must copy to protect parameter phylogeny_df from changes
        phylogeny_df["ancestor_id"]
        .to_numpy()
        .copy()
    )
    phylogeny_df = phylogeny_df.loc[keep_filter].copy()
    phylogeny_df["id"] = original_ids[keep_filter]
    phylogeny_df["ancestor_id"] = original_ids[ancestor_ids[keep_filter]]
    phylogeny_df["ancestor_list"] = alifestd_make_ancestor_list_col(
        phylogeny_df["id"], phylogeny_df["ancestor_id"]
    )

    return phylogeny_df


def alifestd_collapse_unifurcations(
    phylogeny_df: pd.DataFrame,
) -> pd.DataFrame:
    """Pare record to bypass organisms with one ancestor and one descendant.

    Input dataframe is not mutated by this operation.
    """

    if "branch_length" in phylogeny_df or "edge_length" in phylogeny_df:
        warnings.Warning(
            "alifestd_collapse_unifurcations does not update branch length "
            "columns. Use `origin_time` to recalculate branch lengths for "
            "collapsed phylogeny."
        )

    if alifestd_is_asexual(phylogeny_df):
        return _alifestd_collapse_unifurcations_asexual(phylogeny_df)

    if not alifestd_is_topologically_sorted(phylogeny_df):
        phylogeny_df = alifestd_topological_sort(phylogeny_df)

    phylogeny_df = phylogeny_df.set_index("id", drop=False)

    ref_counts = Counter(
        id
        for ancestor_list_str in phylogeny_df["ancestor_list"]
        for id in alifestd_parse_ancestor_ids(ancestor_list_str)
    )

    for id in phylogeny_df["id"]:
        ancestor_ids = alifestd_parse_ancestor_ids(
            phylogeny_df.loc[id, "ancestor_list"]
        )
        if len(ancestor_ids) == 1 and ref_counts[id] == 1:
            # percolate ancestor over self
            (ancestor_id,) = ancestor_ids
            phylogeny_df.loc[id] = phylogeny_df.loc[ancestor_id]
        elif len(ancestor_ids):
            # update referenced ancestor
            phylogeny_df.loc[id, "ancestor_list"] = str(
                [
                    phylogeny_df.loc[ancestor_id, "id"]
                    for ancestor_id in ancestor_ids
                ]
            )

    assert "ancestor_id" not in phylogeny_df

    return phylogeny_df.drop_duplicates().reset_index(drop=True)
