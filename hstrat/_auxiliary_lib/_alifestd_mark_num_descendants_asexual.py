import numpy as np
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_topological_sort import alifestd_topological_sort
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._jit import jit


@jit(nopython=True)
def _alifestd_mark_num_descendants_asexual_fast_path(
    ancestor_ids: np.ndarray,
) -> np.ndarray:
    """Implementation detail for `alifestd_mark_num_descendants_asexual`."""

    num_descendants = np.zeros_like(ancestor_ids)
    for idx_r, ancestor_id in enumerate(ancestor_ids[::-1]):
        idx = len(ancestor_ids) - 1 - idx_r
        if ancestor_id == idx:
            continue  # handle genesis cases

        num_descendants[ancestor_id] += num_descendants[idx] + 1

    return num_descendants


def _alifestd_mark_num_descendants_asexual_slow_path(
    phylogeny_df: pd.DataFrame,
) -> pd.DataFrame:
    """Implementation detail for `alifestd_mark_num_descendants_asexual`."""

    phylogeny_df.index = phylogeny_df["id"]

    phylogeny_df["num_descendants"] = 0

    for idx in reversed(phylogeny_df.index):
        ancestor_id = phylogeny_df.at[idx, "ancestor_id"]
        if ancestor_id == idx:
            continue  # handle genesis cases

        own_num_descendants = phylogeny_df.at[idx, "num_descendants"]

        delta = own_num_descendants + 1
        phylogeny_df.at[ancestor_id, "num_descendants"] += delta

    return phylogeny_df


def alifestd_mark_num_descendants_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add column `num_descendants`, excluding self.

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
            "num_descendants"
        ] = _alifestd_mark_num_descendants_asexual_fast_path(
            phylogeny_df["ancestor_id"].to_numpy()
        )
        return phylogeny_df
    else:
        return _alifestd_mark_num_descendants_asexual_slow_path(phylogeny_df)
