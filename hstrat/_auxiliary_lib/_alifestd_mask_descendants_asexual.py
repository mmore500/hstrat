import numpy as np
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_topological_sort import alifestd_topological_sort
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._jit import jit


@jit(nopython=True)
def alifestd_mask_descendants_asexual_fast_path(
    ancestor_ids: np.ndarray,
    ancestor_mask: np.ndarray,
) -> np.ndarray:
    """Implementation detail for `alifestd_mask_descendants_asexual`."""
    for idx, ancestor_id in enumerate(ancestor_ids):
        ancestor_mask[idx] = ancestor_mask[ancestor_id] | ancestor_mask[idx]

    return ancestor_mask


def alifestd_mask_descendants_asexual_slow_path(
    phylogeny_df: pd.DataFrame,
) -> pd.DataFrame:
    phylogeny_df.index = phylogeny_df["id"]

    for idx in phylogeny_df.index:
        ancestor_id = phylogeny_df.at[idx, "ancestor_id"]

        phylogeny_df.at[idx, "alifestd_mask_descendants_asexual"] = (
            phylogeny_df.at[ancestor_id, "alifestd_mask_descendants_asexual"]
            | phylogeny_df.at[idx, "alifestd_mask_descendants_asexual"]
        )

    return phylogeny_df


def alifestd_mask_descendants_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
    *,
    ancestor_mask: np.ndarray,
) -> pd.DataFrame:
    """For given ancestor nodes, create a mask identifying those nodes and all
    descendants.

    Ancestral nodes are identified by `ancestor_mask` corresponding to rows
    in `phylogeny_df`.

    The mask is returned as a new column `alifestd_mask_descendants_asexual` in
    the output DataFrame.

    A topological sort will be applied if `phylogeny_df` is not topologically
    sorted. Dataframe reindexing (e.g., df.index) may be applied.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    phylogeny_df["alifestd_mask_descendants_asexual"] = ancestor_mask

    if not alifestd_is_topologically_sorted(phylogeny_df):
        phylogeny_df = alifestd_topological_sort(phylogeny_df, mutate=True)

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df[
            "alifestd_mask_descendants_asexual"
        ] = alifestd_mask_descendants_asexual_fast_path(
            phylogeny_df["ancestor_id"].to_numpy(),
            phylogeny_df["alifestd_mask_descendants_asexual"].to_numpy(),
        )
        return phylogeny_df
    else:
        return alifestd_mask_descendants_asexual_slow_path(phylogeny_df)
