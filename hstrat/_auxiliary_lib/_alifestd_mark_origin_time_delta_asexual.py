import pandas as pd

from ._alifestd_mark_ancestor_origin_time_asexual import (
    alifestd_mark_ancestor_origin_time_asexual,
)


def alifestd_mark_origin_time_delta_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add columns `origin_time_delta` and `ancestor_origin_time`.

    Dataframe must provide column `origin_time`.

    A topological sort will be applied if `phylogeny_df` is not topologically
    sorted. Dataframe reindexing (e.g., df.index) may be applied.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_mark_ancestor_origin_time_asexual(
        phylogeny_df, mutate=True
    )

    phylogeny_df["origin_time_delta"] = (
        phylogeny_df["origin_time"] - phylogeny_df["ancestor_origin_time"]
    )

    return phylogeny_df
