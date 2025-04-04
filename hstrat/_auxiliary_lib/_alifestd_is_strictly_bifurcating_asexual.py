import numpy as np
import pandas as pd

from ._alifestd_to_working_format import alifestd_to_working_format
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def alifestd_is_strictly_bifurcating_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> bool:
    """Are all organisms listed after members of their `ancestor_list`?

    Input dataframe is not mutated by this operation.
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    phylogeny_df = alifestd_to_working_format(phylogeny_df, mutate=True)

    is_root = phylogeny_df["id"] == phylogeny_df["ancestor_id"]
    __, counts = np.unique(
        phylogeny_df.loc[~is_root, "ancestor_id"], return_counts=True
    )
    return np.all(counts == 2)
