import itertools as it
import typing
import warnings

import pandas as pd
import sortedcontainers as sc

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_has_multiple_roots import alifestd_has_multiple_roots
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_mark_leaves import alifestd_mark_leaves
from ._alifestd_topological_sort import alifestd_topological_sort
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def alifestd_mark_ot_mrca_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
    progress_wrap: typing.Callable = lambda x: x,
) -> pd.DataFrame:
    """Add columns `ot_mrca_id`, `ot_mrca_time_of`, and `ot_mrca_time_since`,
    giving information about mrca of extant organisms at organism `origin_time`.

    A chronological sort will be applied if `phylogeny_df` is not
    chronologically sorted. Reindexing may be applied.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """

    # setup
    if alifestd_has_multiple_roots(phylogeny_df):
        raise NotImplementedError()

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)
    if not alifestd_is_topologically_sorted(phylogeny_df):
        phylogeny_df = alifestd_topological_sort(phylogeny_df, mutate=True)
    phylogeny_df = alifestd_mark_leaves(phylogeny_df, mutate=True)

    contig = alifestd_has_contiguous_ids(phylogeny_df)
    if contig:
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        warnings.warn("mark_ot_mrca_asexual may be slow with uncontiguous ids")
        phylogeny_df.index = phylogeny_df["id"]

    phylogeny_df["ot_mrca_id"] = phylogeny_df["id"].max() + 1
    phylogeny_df["ot_mrca_time_of"] = phylogeny_df["origin_time"].max()
    phylogeny_df["ot_mrca_time_since"] = phylogeny_df["origin_time"].max()

    df = phylogeny_df
    df["bwd_origin_time"] = -df["origin_time"]

    # do calculation
    running_mrca_id = max(
        df["id"],
        default=None,
        key=lambda i: (df.at[i, "origin_time"], df.index.get_loc(i)),
    )  # initial value

    # for optimization
    ot_mrca_ids = []
    ot_mrca_times_of = []
    ot_mrca_times_since = []
    indices = []
    key = df.index.get_loc if not contig else None
    for bwd_origin_time, group in progress_wrap(df.groupby("bwd_origin_time")):
        earliest_id = (
            group["id"].min() if contig else min(group["id"], key=key)
        )

        leaf_mask = group["is_leaf"]
        lineages = sc.SortedSet(
            (*group.loc[leaf_mask, "id"], earliest_id, running_mrca_id),
            key=key,
        )
        while len(lineages) > 1:
            oldest = lineages.pop(-1)
            replacement = df.at[oldest, "ancestor_id"]
            assert replacement != oldest
            lineages.add(replacement)

        (mrca_id,) = lineages
        running_mrca_id = mrca_id

        # set column values
        mrca_time = df.at[mrca_id, "origin_time"]

        size = len(group)
        indices.extend(group["id"])
        ot_mrca_ids.extend(it.repeat(mrca_id, size))
        ot_mrca_times_of.extend(it.repeat(mrca_time, size))
        ot_mrca_times_since.extend(
            it.repeat(-bwd_origin_time - mrca_time, size),
        )

    df.loc[indices, "ot_mrca_id"] = ot_mrca_ids
    df.loc[indices, "ot_mrca_time_of"] = ot_mrca_times_of
    df.loc[indices, "ot_mrca_time_since"] = ot_mrca_times_since
    df.drop("bwd_origin_time", axis=1, inplace=True)
    return df
