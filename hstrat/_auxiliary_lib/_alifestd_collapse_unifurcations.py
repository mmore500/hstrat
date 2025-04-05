from collections import Counter
import logging
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
from ._jit_numpy_uint8_t import jit_numpy_uint8_t


@jit(nopython=True)
def _collapse_unifurcations(
    ancestor_ids: np.ndarray,
) -> typing.Tuple[np.ndarray, np.ndarray]:
    # assumes contiguous ids

    ref_counts = np.zeros(len(ancestor_ids), dtype=jit_numpy_uint8_t)
    for ancestor_id in ancestor_ids:
        # cap to prevent overflow
        ref_counts[ancestor_id] = min(ref_counts[ancestor_id] + 1, 2)

    ids = np.arange(len(ancestor_ids))

    for pos, ancestor_id in enumerate(ancestor_ids):
        id_ = ids[pos]
        assert id_ == pos
        assert ancestor_id <= id_

        if ref_counts[ancestor_id] == 1:  # root ok
            # percolate ancestor over self
            ancestor_ids[pos] = ancestor_ids[ancestor_id]

    keep_filter = (ref_counts != 1) | (ancestor_ids == ids)

    return keep_filter, ancestor_ids


def _alifestd_collapse_unifurcations_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool,
    root_ancestor_token: str,
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

    logging.info("- alifestd_collapse_unifurcations: calculating reindex...")
    assert (phylogeny_df["id"] >= phylogeny_df["ancestor_id"]).all()
    keep_filter, ancestor_ids = _collapse_unifurcations(
        phylogeny_df["ancestor_id"].to_numpy(),
    )

    logging.info("- alifestd_collapse_unifurcations: applying reindex...")
    phylogeny_df = phylogeny_df.loc[keep_filter].copy()
    phylogeny_df["id"] = original_ids[keep_filter]
    phylogeny_df["ancestor_id"] = original_ids[ancestor_ids[keep_filter]]
    if "ancestor_list" in phylogeny_df:
        phylogeny_df.loc[:, "ancestor_list"] = alifestd_make_ancestor_list_col(
            phylogeny_df["id"],
            phylogeny_df["ancestor_id"],
            root_ancestor_token=root_ancestor_token,
        )

    return phylogeny_df


def alifestd_collapse_unifurcations(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
    root_ancestor_token: str = "none",
) -> pd.DataFrame:
    """Pare record to bypass organisms with one ancestor and one descendant.

    May leave a root unifurcation present. See
    `alifestd_delete_unifurcating_roots_asexual`.

    The option `root_ancestor_token` will be sandwiched in brackets to create
    the ancestor list entry for genesis organisms. For example, the token
    "None" will yield the entry "[None]" and the token "" will yield the entry
    "[]". Default "none".

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """

    if any(
        col in phylogeny_df
        for col in ["branch_length", "edge_length", "origin_time_delta"]
    ):
        warnings.warn(
            "alifestd_collapse_unifurcations does not update branch length "
            "columns. Use `origin_time` to recalculate branch lengths for "
            "collapsed phylogeny."
        )

    # special optimized handling for asexual phylogenies
    if alifestd_is_asexual(phylogeny_df):
        return _alifestd_collapse_unifurcations_asexual(
            phylogeny_df,
            mutate=mutate,
            root_ancestor_token=root_ancestor_token,
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
                    int(phylogeny_df.loc[ancestor_id, "id"])
                    for ancestor_id in ancestor_ids
                ]
            )
        else:
            assert not ancestor_ids
            phylogeny_df.loc[id_, "ancestor_list"] = f"[{root_ancestor_token}]"

    assert "ancestor_id" not in phylogeny_df

    return phylogeny_df.drop_duplicates().reset_index(drop=True)
