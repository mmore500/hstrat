import pandas as pd

from ._alifestd_mark_num_children_asexual import (
    alifestd_mark_num_children_asexual,
)
from ._alifestd_mark_roots import alifestd_mark_roots


def alifestd_count_unifurcating_roots_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> int:
    """How many root nodes with one child are contained in phylogeny?"""

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_mark_num_children_asexual(
        phylogeny_df, mutate=True
    )
    phylogeny_df = alifestd_mark_roots(phylogeny_df, mutate=True)

    return (
        phylogeny_df["is_root"] & (phylogeny_df["num_children"] == 1)
    ).sum()
