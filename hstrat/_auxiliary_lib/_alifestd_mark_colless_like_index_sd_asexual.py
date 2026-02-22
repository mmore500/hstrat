import pandas as pd

from ._alifestd_mark_colless_like_index_mdm_asexual import (
    _alifestd_mark_colless_like_index_asexual_impl,
)


def alifestd_mark_colless_like_index_sd_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add column `colless_like_index_sd` with Colless-like index
    using sample standard deviation as dissimilarity.

    Computes the Colless-like balance index from Mir, Rossello, and
    Rotger (2018) that supports polytomies. Uses weight function
    f(k) = ln(k + e) and standard deviation dissimilarity.

    For each internal node v with children v_1, ..., v_k:
        bal(v) = sd(delta_f(T_v1), ..., delta_f(T_vk))

    where delta_f(T) is the f-size of subtree T, defined as the sum
    of f(deg(u)) over all nodes u in T, and

        sd(x_1, ..., x_k) = sqrt(var(x_1, ..., x_k))
        var(x_1, ..., x_k) = (1/(k-1)) * sum (x_i - mean(x))^2

    The Colless-like index at a node is the sum of balance values
    across all internal nodes in its subtree.

    Leaf nodes will have Colless-like index 0. The root node contains
    the Colless-like index for the entire tree.

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
        "colless_like_index_sd" containing the Colless-like
        imbalance index for the subtree rooted at each node.

    References
    ----------
    Mir, A., Rossello, F., & Rotger, L. (2018). Sound Colless-like
    balance indices for multifurcating trees. PLOS ONE, 13(9),
    e0203401. https://doi.org/10.1371/journal.pone.0203401

    See Also
    --------
    alifestd_mark_colless_like_index_mdm_asexual :
        Colless-like index using MDM dissimilarity.
    alifestd_mark_colless_like_index_var_asexual :
        Colless-like index using variance dissimilarity.
    alifestd_mark_colless_index_asexual :
        Classic Colless index for strictly bifurcating trees.
    """
    return _alifestd_mark_colless_like_index_asexual_impl(
        phylogeny_df,
        "colless_like_index_sd",
        "sd",
        mutate=mutate,
    )
