import numpy as np
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def alifestd_calc_clade_lookback_n_asexual(
    phylogeny_df: pd.DataFrame,
    lookback_n: int,
    mutate: bool = False,
) -> np.ndarray:
    """Find ancestor ids of nodes that are `lookback_n` nodes away in the
    phylogeny.

    The root node will be returned if the lookback distance exceeds available
    nodes.

    Returns a numpy array of the same length as the input DataFrame, with array
    elements as the number of nodes in the clade that have the trait. Returned
    array matches row order of the input DataFrame.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.index = phylogeny_df["id"]

    lookback_result = phylogeny_df["id"].values.copy()
    for __ in range(lookback_n):
        lookback_result = phylogeny_df.loc[
            lookback_result, "ancestor_id"
        ].values.copy()

    return lookback_result
