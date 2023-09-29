import itertools as it

import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_has_multiple_roots import alifestd_has_multiple_roots
from ._alifestd_mark_leaves import alifestd_mark_leaves
from ._alifestd_is_chronologically_sorted import (
    alifestd_is_chronologically_sorted,
)
from ._alifestd_chronological_sort import alifestd_chronological_sort
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._alifestd_unfurl_lineage_asexual import alifestd_unfurl_lineage_asexual


def alifestd_mark_ot_mrca_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
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
    if not alifestd_is_chronologically_sorted(phylogeny_df):
        phylogeny_df = alifestd_chronological_sort(phylogeny_df, mutate=True)
    phylogeny_df = alifestd_mark_leaves(phylogeny_df, mutate=True)

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.index = phylogeny_df["id"]

    phylogeny_df["ot_mrca_id"] = phylogeny_df["id"].max() + 1
    phylogeny_df["ot_mrca_time_of"] = phylogeny_df["origin_time"].max()
    phylogeny_df["ot_mrca_time_since"] = phylogeny_df["origin_time"].max()

    df = phylogeny_df

    # do calculation
    assert df["origin_time"].is_monotonic_increasing
    reverse_index = reversed(df.index)
    groups = it.groupby(
        reverse_index,
        lambda v: df.loc[v, "origin_time"],
    )

    running_mrca_id = max(
        df["id"], default=None, key=lambda i: df.loc[i, "origin_time"]
    )
    for _origin_time, indices in groups:
        group_mask = df.index.isin(indices)
        earliest_id = min(
            df.loc[group_mask, "id"], key=lambda i: df.loc[i, "origin_time"]
        )
        leaf_mask = group_mask & df["is_leaf"]

        lineages = [
            {*alifestd_unfurl_lineage_asexual(df, leaf_id, mutate=True)}
            for leaf_id in {
                *df.loc[leaf_mask, "id"],
                earliest_id,
                running_mrca_id,
            }
        ]
        assert len(lineages)

        mrca_id = max(
            set.intersection(*lineages), key=lambda i: df.loc[i, "origin_time"]
        )
        running_mrca_id = mrca_id

        # set column values
        df.loc[group_mask, "ot_mrca_id"] = mrca_id

        mrca_time = df.loc[mrca_id, "origin_time"]
        df.loc[group_mask, "ot_mrca_time_of"] = mrca_time
        df.loc[group_mask, "ot_mrca_time_since"] = (
            df.loc[group_mask, "origin_time"] - mrca_time
        )

    return df
