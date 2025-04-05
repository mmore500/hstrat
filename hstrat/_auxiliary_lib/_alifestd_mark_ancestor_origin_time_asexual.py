import numpy as np
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_topological_sort import alifestd_topological_sort
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._jit import jit


@jit(nopython=True)
def _alifestd_get_ancestor_origin_time_asexual_contiguous(
    ancestor_ids: np.ndarray,
    origin_times: np.ndarray,
) -> np.ndarray:
    """Optimized implementation for asexual phylogenies with contiguous ids."""
    ancestor_ids = ancestor_ids.astype(np.uint64)
    ancestor_origin_times = np.empty_like(origin_times)

    for id_, _ in enumerate(ancestor_ids):
        ancestor_id = ancestor_ids[id_]
        ancestor_origin_time = origin_times[ancestor_id]
        ancestor_origin_times[id_] = ancestor_origin_time

    return ancestor_origin_times


def alifestd_mark_ancestor_origin_time_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add column `ancestor_origin_time`.

    Dataframe must provide column `origin_time`.

    A topological sort will be applied if `phylogeny_df` is not topologically
    sorted. Dataframe reindexing (e.g., df.index) may be applied.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if "origin_time" not in phylogeny_df.columns:
        raise ValueError("Column 'origin_time' not found in dataframe.")

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if not alifestd_is_topologically_sorted(phylogeny_df):
        phylogeny_df = alifestd_topological_sort(phylogeny_df, mutate=True)

    if alifestd_has_contiguous_ids(phylogeny_df) and not phylogeny_df.empty:
        # optimized implementation for contiguous ids
        phylogeny_df[
            "ancestor_origin_time"
        ] = _alifestd_get_ancestor_origin_time_asexual_contiguous(
            phylogeny_df["ancestor_id"].values,
            phylogeny_df["origin_time"].values,
        )
        return phylogeny_df

    # slower fallback implementation
    phylogeny_df.index = phylogeny_df["id"]

    phylogeny_df["ancestor_origin_time"] = 0

    for idx in reversed(phylogeny_df.index):
        ancestor_id = phylogeny_df.loc[idx, "ancestor_id"]
        ancestor_origin_time = phylogeny_df.loc[ancestor_id, "origin_time"]
        phylogeny_df.loc[idx, "ancestor_origin_time"] = ancestor_origin_time

    return phylogeny_df
