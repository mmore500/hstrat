import numpy as np
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def alifestd_calc_clade_lookback_origin_time_delta_asexual(
    phylogeny_df: pd.DataFrame,
    lookback_origin_time_delta: float,
    mutate: bool = False,
) -> np.ndarray:
    """Find ancestor ids of nodes that precede each phylogeny node by at least
    `lookback_origin_time_delta` branch distance.

    The root node will be returned if the lookback distance exceeds available
    nodes.

    Returns a numpy array of the same length as the input DataFrame, with array
    elements as the number of nodes in the clade that have the trait. Returned
    array matches row order of the input DataFrame.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if "origin_time" not in phylogeny_df.columns:
        raise ValueError("Dataframe must provide column `origin_time`.")

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.index = phylogeny_df["id"]

    lookback_result = phylogeny_df["id"].values.copy()
    while True:
        ot_delta = (
            phylogeny_df["origin_time"].values
            - phylogeny_df.loc[lookback_result, "origin_time"].values
        )
        should_lookback = ot_delta < lookback_origin_time_delta
        if np.all(~should_lookback) or np.array_equal(
            phylogeny_df.loc[
                lookback_result[should_lookback], "ancestor_id"
            ].values,
            phylogeny_df.loc[lookback_result[should_lookback], "id"].values,
        ):
            break

        lookback_result[should_lookback] = phylogeny_df.loc[
            lookback_result[should_lookback], "ancestor_id"
        ].values

    return lookback_result
