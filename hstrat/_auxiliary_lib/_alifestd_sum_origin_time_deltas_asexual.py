import numbers

import pandas as pd

from ._alifestd_mark_origin_time_delta_asexual import (
    alifestd_mark_origin_time_delta_asexual,
)


def alifestd_sum_origin_time_deltas_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> numbers.Number:
    """Sum differences between taxa origin times and their ancestors' origin
    time.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    """

    if "origin_time_delta" not in phylogeny_df.columns:
        if not mutate:
            phylogeny_df = phylogeny_df.copy()

        phylogeny_df = alifestd_mark_origin_time_delta_asexual(
            phylogeny_df, mutate=True
        )

    return phylogeny_df["origin_time_delta"].sum()
