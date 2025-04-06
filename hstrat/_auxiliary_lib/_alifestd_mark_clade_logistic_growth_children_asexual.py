from joblib import Parallel, delayed, parallel_backend
import numpy as np
import pandas as pd
import sklearn

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_strictly_bifurcating_asexual import (
    alifestd_is_strictly_bifurcating_asexual,
)
from ._alifestd_mark_leaves import alifestd_mark_leaves
from ._alifestd_mark_node_depth_asexual import alifestd_mark_node_depth_asexual
from ._alifestd_unfurl_traversal_inorder_asexual import (
    alifestd_unfurl_traversal_inorder_asexual,
)
from ._warn_once import warn_once


def alifestd_mark_clade_logistic_growth_children_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add column `clade_logistic_growth_children`, containing the coefficient
    of a logistic regression fit to origin times of the leaf descendants of
    each node.

    Nodes with left/right child clades with equal growth rates will have value
    approximately 0.0. If left child clade has greater growth rate, value will
    be negative. If right child clade has greater growth rate, value will be positive.

    Leaf nodes will have value NaN.

    Tree must be strictly bifurcating and single-rooted.

    Dataframe reindexing (e.g., df.index) may be applied.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.

    References
    ----------
    Bonetti Franceschi V and Volz E. Phylogenetic signatures reveal
        multilevel selection and fitness costs in SARS-CoV-2 [version 2; peer
        review: 2 approved, 1 approved with reservations]. Wellcome Open Res
        2024, 9:85 (https://doi.org/10.12688/wellcomeopenres.20704.2)

    Volz, E. Fitness, growth and transmissibility of SARS-CoV-2 genetic
        variants. Nat Rev Genet 24, 724-734 (2023).
        https://doi.org/10.1038/s41576-023-00610-z
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if not alifestd_is_strictly_bifurcating_asexual(phylogeny_df):
        raise ValueError("phylogeny_df must be strictly bifurcating")

    if "origin_time" not in phylogeny_df.columns:
        raise ValueError("phylogeny_df must contain `origin_time` column")

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.index = phylogeny_df["id"]

    if "node_depth" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_node_depth_asexual(
            phylogeny_df, mutate=True
        )

    if "is_leaf" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_leaves(phylogeny_df, mutate=True)

    inorder_traversal = alifestd_unfurl_traversal_inorder_asexual(
        phylogeny_df, mutate=True
    )

    leaves = phylogeny_df.loc[inorder_traversal, "is_leaf"].values
    leaves = leaves.astype(float, copy=True)  # contiguous for perf

    node_depths = phylogeny_df.loc[inorder_traversal, "node_depth"].values
    node_depths = node_depths.copy()  # contiguous for perf

    origin_times = phylogeny_df.loc[inorder_traversal, "origin_time"].values
    origin_times = origin_times.astype(float, copy=True)  # contiguous for perf

    for arr in (leaves, node_depths, origin_times):  # probably not needed?
        arr.flags.writeable = False

    def fit_logistic_regression(target_idx: int) -> float:
        target_depth = node_depths[target_idx]
        lb_exclusive = next(
            (
                i
                for i in reversed(range(0, target_idx))
                if node_depths[i] <= target_depth
            ),
            -1,
        )
        lb_inclusive = lb_exclusive + 1
        ub_exclusive = next(
            (
                i
                for i in range(target_idx + 1, len(node_depths))
                if node_depths[i] <= target_depth
            ),
            len(node_depths),
        )
        slice_ = slice(lb_inclusive, ub_exclusive)
        sliced_target = target_idx - slice_.start

        if ub_exclusive - lb_inclusive <= 1:
            return np.nan

        assert lb_inclusive < target_idx < ub_exclusive - 1

        # predictor values; reshape to (N x 1) array for sklearn
        X = origin_times[slice_].reshape(-1, 1, copy=False)

        # sample weights; exclude target node and internal nodes
        assert leaves[target_idx] == 0.0
        w = leaves[slice_]

        # classification target (response); 0 for left clade, 1 for right clade
        y = np.zeros(len(X), dtype=int)
        y[sliced_target:] = 1

        model = sklearn.linear_model.LogisticRegression()
        model.fit(X=X, y=y, sample_weight=w)
        res = model.coef_[0][0]
        if np.isnan(res):
            warn_once("clade logistic growth regression produced NaN")
        return res

    # scikit wants threading backend
    # see https://scikit-learn.org/stable/computing/parallelism.html#higher-level-parallelism-with-joblib
    with parallel_backend("threading", n_jobs=-1):
        results = Parallel(n_jobs=-1)(
            delayed(fit_logistic_regression)(i)
            for i in range(len(node_depths))
        )

    assert len(results) == len(node_depths)
    phylogeny_df["clade_logistic_growth_children"] = pd.Series(
        results, index=inorder_traversal, dtype=float
    )

    return phylogeny_df
