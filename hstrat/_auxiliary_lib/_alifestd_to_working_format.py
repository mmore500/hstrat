import pandas as pd

from ._alifestd_assign_contiguous_ids import alifestd_assign_contiguous_ids
from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_topological_sort import alifestd_topological_sort
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def alifestd_to_working_format(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Re-encode phylogeny_df to facilitate efficient analysis and
    transformation operations.

    The returned phylogeny dataframe will
    * be topologically sorted (i.e., organisms appear after all ancestors),
    * have contiguous ids (i.e., organisms' ids correspond to row number),
    * contain an integer datatype `ancestor_id` column if the phylogeny is
    asexual (i.e., a more performant representation of `ancestor_list`).

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if not alifestd_is_topologically_sorted(phylogeny_df):
        phylogeny_df = alifestd_topological_sort(phylogeny_df, mutate=True)

    if not alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df = alifestd_assign_contiguous_ids(
            phylogeny_df, mutate=True
        )

    return phylogeny_df
