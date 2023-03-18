import pandas as pd

from ._alifestd_find_chronological_inconsistency import (
    alifestd_find_chronological_inconsistency,
)


def alifestd_is_chronologically_ordered(phylogeny_df: pd.DataFrame) -> bool:
    """Are all organisms listed after members of their `ancestor_list`?

    Input dataframe is not mutated by this operation.
    """

    return alifestd_find_chronological_inconsistency(phylogeny_df) is None
