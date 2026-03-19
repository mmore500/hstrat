from deprecated.sphinx import deprecated
import pandas as pd

from ._alifestd_is_sexual import alifestd_is_sexual


@deprecated(
    version="1.23.0",
    reason="Use phyloframe.legacy.alifestd_is_asexual instead.",
)
def alifestd_is_asexual(phylogeny_df: pd.DataFrame) -> bool:
    """Do all organisms in the phylogeny have one or no immediate ancestor?

    Input dataframe is not mutated by this operation.
    """
    return "ancestor_id" in phylogeny_df or not alifestd_is_sexual(
        phylogeny_df
    )
