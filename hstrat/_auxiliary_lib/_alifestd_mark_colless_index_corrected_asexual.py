import numpy as np
import pandas as pd

from ._alifestd_mark_colless_index_asexual import (
    alifestd_mark_colless_index_asexual,
)
from ._alifestd_mark_num_leaves_asexual import (
    alifestd_mark_num_leaves_asexual,
)


def alifestd_mark_colless_index_corrected_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add column `colless_index_corrected` with the corrected Colless
    index for each subtree.

    The corrected Colless index IC(T) normalizes the Colless index by
    tree size. For a subtree with n leaves:

        IC(T) = 0                          if n <= 2
        IC(T) = 2 * C(T) / ((n-1)*(n-2))  if n > 2

    where C(T) is the Colless index of the subtree.

    This function delegates to `alifestd_mark_colless_index_asexual` to
    compute the Colless index, and therefore requires strictly
    bifurcating trees.

    Raises ValueError if the tree is not strictly bifurcating. For
    trees with polytomies, consider computing the generalized Colless
    index and normalizing separately.

    A topological sort will be applied if `phylogeny_df` is not
    topologically sorted. Dataframe reindexing (e.g., df.index) may
    be applied.

    Input dataframe is not mutated by this operation unless `mutate`
    set True. If mutate set True, operation does not occur in place;
    still use return value to get transformed phylogeny dataframe.

    Parameters
    ----------
    phylogeny_df : pd.DataFrame
        Alife standard DataFrame containing the phylogenetic
        relationships.

    mutate : bool, optional
        If True, modify the input DataFrame in place. Default is
        False.

    Returns
    -------
    pd.DataFrame
        Phylogeny DataFrame with an additional column
        "colless_index_corrected" containing the corrected Colless
        imbalance index for the subtree rooted at each node.

    Raises
    ------
    ValueError
        If phylogeny_df is not strictly bifurcating.

    See Also
    --------
    alifestd_mark_colless_index_asexual :
        Unnormalized Colless index for strictly bifurcating trees.
    alifestd_mark_colless_index_generalized_asexual :
        Generalized Colless index that supports polytomies.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if len(phylogeny_df) == 0:
        phylogeny_df["colless_index_corrected"] = pd.Series(
            dtype=float,
        )
        return phylogeny_df

    if "colless_index" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_colless_index_asexual(
            phylogeny_df, mutate=True
        )

    if "num_leaves" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_num_leaves_asexual(
            phylogeny_df, mutate=True
        )

    n = phylogeny_df["num_leaves"].to_numpy(dtype=np.float64)
    c = phylogeny_df["colless_index"].to_numpy(dtype=np.float64)

    denom = (n - 1.0) * (n - 2.0)
    safe_denom = np.where(denom > 0, denom, 1.0)
    corrected = np.where(n > 2, 2.0 * c / safe_denom, 0.0)
    phylogeny_df["colless_index_corrected"] = corrected

    return phylogeny_df
