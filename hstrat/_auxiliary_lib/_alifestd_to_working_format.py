import pandas as pd

from ._alifestd_assign_contiguous_ids import alifestd_assign_contiguous_ids
from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_asexual import alifestd_is_asexual
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_make_ancestor_id_col import alifestd_make_ancestor_id_col
from ._alifestd_parse_ancestor_id import alifestd_parse_ancestor_id
from ._alifestd_topological_sort import alifestd_topological_sort


def alifestd_to_working_format(phylogeny_df: pd.DataFrame) -> pd.DataFrame:
    """Re-encode phylogeny_df to facilitate efficient analysis and
    transformation operations.

    The returned phylogeny dataframe will
    * be topologically sorted (i.e., organisms appear after all ancestors),
    * have contiguous ids (i.e., organisms' ids correspond to row number),
    * contain an integer datatype `ancestor_id` column if the phylogeny is
    asexual (i.e., a more performant representation of `ancestor_list`).

    Input dataframe is not mutated by this operation.
    """
    is_copy = False

    if not alifestd_is_topologically_sorted(phylogeny_df):
        is_copy = True
        phylogeny_df = alifestd_topological_sort(phylogeny_df)

    if not alifestd_has_contiguous_ids(phylogeny_df):
        is_copy = True
        phylogeny_df = alifestd_assign_contiguous_ids(phylogeny_df)

    if "ancestor_id" not in phylogeny_df and alifestd_is_asexual(phylogeny_df):
        if not is_copy:
            phylogeny_df = phylogeny_df.copy()
        phylogeny_df["ancestor_id"] = alifestd_make_ancestor_id_col(
            phylogeny_df["id"], phylogeny_df["ancestor_list"]
        )

    return phylogeny_df
