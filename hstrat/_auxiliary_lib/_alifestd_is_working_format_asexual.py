import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted


def alifestd_is_working_format_asexual(
    phylogeny_df,
    mutate: bool = False,
) -> pd.DataFrame:
    """Test if phylogeny_df is an asexual phylogeny in working format.

    The working format is a dataframe with the following properties:
      - topologically sorted (i.e., organisms appear after all ancestors),
      - contiguous ids (i.e., organisms' ids correspond to row number), and
      - contains an integer datatype `ancestor_id` column.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    return (
        "ancestor_id" in phylogeny_df.columns
        and alifestd_is_topologically_sorted(phylogeny_df)
        and alifestd_has_contiguous_ids(phylogeny_df)
    )
