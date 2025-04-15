import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_mark_num_leaves_asexual import alifestd_mark_num_leaves_asexual
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col


def alifestd_mark_num_leaves_sibling_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Mark the number of leaves descendant from each node's siblings.

    Nodes with no siblings (e.g., root nodes) will have value 0 marked.

    Parameters
    ----------
    phylogeny_df : pd.DataFrame
        Alife standard DataFrame containing the phylogenetic relationships.

    mutate : bool, optional
        If True, modify the input DataFrame in place. Default is False.

    Returns
    -------
    pd.DataFrame
        Phylogeny DataFrame with an additional column "num_leaves_sibling"
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if "num_leaves" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_num_leaves_asexual(
            phylogeny_df, mutate=True
        )

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.index = phylogeny_df["id"]

    phylogeny_df["num_leaves_sibling"] = (
        phylogeny_df.loc[
            phylogeny_df["ancestor_id"],
            "num_leaves",
        ].values
        - phylogeny_df["num_leaves"].values
    )

    return phylogeny_df
