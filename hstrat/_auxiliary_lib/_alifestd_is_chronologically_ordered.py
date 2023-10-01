import pandas as pd

from ._alifestd_find_chronological_inconsistency import (
    alifestd_find_chronological_inconsistency,
)


def alifestd_is_chronologically_ordered(phylogeny_df: pd.DataFrame) -> bool:
    """Do any organisms have `origin_time`s preceding membersof their
    `ancestor_list`?

    Input dataframe is not mutated by this operation.
    """

    return alifestd_find_chronological_inconsistency(phylogeny_df) is None
