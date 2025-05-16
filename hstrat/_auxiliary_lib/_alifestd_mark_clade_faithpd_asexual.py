import numpy as np
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_mark_origin_time_delta_asexual import (
    alifestd_mark_origin_time_delta_asexual,
)
from ._alifestd_topological_sort import alifestd_topological_sort
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._jit import jit


@jit(nopython=True)
def alifestd_mark_clade_faithpd_asexual_fast_path(
    ancestor_ids: np.ndarray,
    origin_time_deltas: np.ndarray,
) -> np.ndarray:
    """Implementation detail for `alifestd_mark_clade_faithpd_asexual`."""

    clade_faithpds = np.zeros_like(origin_time_deltas)
    for idx_r, ancestor_id in enumerate(ancestor_ids[::-1]):
        idx = len(ancestor_ids) - 1 - idx_r
        if ancestor_id == idx:
            continue  # handle root cases

        clade_faithpds[ancestor_id] += (
            origin_time_deltas[idx] + clade_faithpds[idx]
        )

    return clade_faithpds


def alifestd_mark_clade_faithpd_asexual_slow_path(
    phylogeny_df: pd.DataFrame,
) -> pd.DataFrame:
    """Implementation detail for `alifestd_mark_clade_faithpd_asexual`."""
    phylogeny_df.index = phylogeny_df["id"]

    phylogeny_df["clade_faithpd"] = 0

    for idx in reversed(phylogeny_df.index):
        ancestor_id = phylogeny_df.at[idx, "ancestor_id"]
        if ancestor_id == idx:
            continue  # handle root cases

        phylogeny_df.at[ancestor_id, "clade_faithpd"] += (
            phylogeny_df.at[idx, "origin_time_delta"]
            + phylogeny_df.at[idx, "clade_faithpd"]
        )

    return phylogeny_df


def alifestd_mark_clade_faithpd_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add column `clade_faithpd`, containing sum branch length among
    descendant noes.

    Branch length is defined as the difference between the origin time
    of the node and the origin time of its ancestor.

    A topological sort will be applied if `phylogeny_df` is not topologically
    sorted. Dataframe reindexing (e.g., df.index) may be applied.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if not alifestd_is_topologically_sorted(phylogeny_df):
        phylogeny_df = alifestd_topological_sort(phylogeny_df, mutate=True)

    if "origin_time_delta" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_origin_time_delta_asexual(
            phylogeny_df, mutate=True
        )

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df[
            "clade_faithpd"
        ] = alifestd_mark_clade_faithpd_asexual_fast_path(
            pd.to_numeric(phylogeny_df["ancestor_id"]).to_numpy(),
            pd.to_numeric(phylogeny_df["origin_time_delta"]).to_numpy(),
        )
        return phylogeny_df
    else:
        return alifestd_mark_clade_faithpd_asexual_slow_path(
            phylogeny_df,
        )
