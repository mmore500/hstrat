import numpy as np
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_topological_sort import alifestd_topological_sort
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._jit import jit


@jit(nopython=True)
def alifestd_mark_max_descendant_origin_time_asexual_fast_path(
    ancestor_ids: np.ndarray,
    origin_times: np.ndarray,
) -> np.ndarray:
    """Implementation detail for `alifestd_mark_max_descendant_origin_time_asexual`."""

    max_descendant_origin_times = np.copy(origin_times)
    for idx_r, ancestor_id in enumerate(ancestor_ids[::-1]):
        idx = len(ancestor_ids) - 1 - idx_r
        if ancestor_id == idx:
            continue  # handle root cases

        own_max = max_descendant_origin_times[idx]
        max_descendant_origin_times[ancestor_id] = max(
            own_max, max_descendant_origin_times[ancestor_id]
        )

    return max_descendant_origin_times


def alifestd_mark_max_descendant_origin_time_asexual_slow_path(
    phylogeny_df: pd.DataFrame,
) -> pd.DataFrame:
    """Implementation detail for `alifestd_mark_max_descendant_origin_time_asexual`."""
    phylogeny_df.index = phylogeny_df["id"]

    phylogeny_df["max_descendant_origin_time"] = phylogeny_df["origin_time"]

    for idx in reversed(phylogeny_df.index):
        ancestor_id = phylogeny_df.at[idx, "ancestor_id"]
        if ancestor_id == idx:
            continue  # handle root cases

        own_max = phylogeny_df.at[idx, "max_descendant_origin_time"]

        phylogeny_df.at[ancestor_id, "max_descendant_origin_time"] = max(
            own_max,
            phylogeny_df.at[ancestor_id, "max_descendant_origin_time"],
        )

    return phylogeny_df


def alifestd_mark_max_descendant_origin_time_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add column `max_descendant_origin_time`, excluding self.

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

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df[
            "max_descendant_origin_time"
        ] = alifestd_mark_max_descendant_origin_time_asexual_fast_path(
            pd.to_numeric(phylogeny_df["ancestor_id"]).to_numpy(),
            pd.to_numeric(phylogeny_df["origin_time"]).to_numpy(),
        )
        return phylogeny_df
    else:
        return alifestd_mark_max_descendant_origin_time_asexual_slow_path(
            phylogeny_df,
        )
