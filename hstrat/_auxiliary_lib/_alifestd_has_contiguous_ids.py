from deprecated.sphinx import deprecated
import numpy as np
import pandas as pd


@deprecated(
    version="1.23.0",
    reason="Use phyloframe.legacy.alifestd_has_contiguous_ids instead.",
)
def alifestd_has_contiguous_ids(phylogeny_df: pd.DataFrame) -> bool:
    """Do organisms ids' correspond to their row number?

    Input dataframe is not mutated by this operation.
    """
    return (
        phylogeny_df["id"].to_numpy() == np.arange(len(phylogeny_df))
    ).all()
