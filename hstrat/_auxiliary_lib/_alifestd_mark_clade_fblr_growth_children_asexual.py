import contextlib
import typing

import joblib
import numpy as np
import pandas as pd

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_strictly_bifurcating_asexual import (
    alifestd_is_strictly_bifurcating_asexual,
)
from ._alifestd_mark_clade_logistic_growth_children_asexual import (
    _calc_boundaries,
)
from ._alifestd_mark_leaves import alifestd_mark_leaves
from ._alifestd_mark_node_depth_asexual import alifestd_mark_node_depth_asexual
from ._alifestd_unfurl_traversal_inorder_asexual import (
    alifestd_unfurl_traversal_inorder_asexual,
)
from ._fit_fblr import fit_fblr
from ._warn_once import warn_once


def alifestd_mark_clade_fblr_growth_children_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
    *,
    parallel_backend: typing.Optional[str] = None,
    progress_wrap: typing.Callable = lambda x: x,
    work_mask: typing.Optional[np.ndarray] = None,
) -> pd.DataFrame:
    """Add column `clade_fblr_growth_children`, containing the coefficient
    of a fblr regression fit to origin times of the leaf descendants of
    each node.

    Nodes with left/right child clades with equal growth rates will have value
    approximately 0.0. If left child clade has greater growth rate, value will
    be negative. If right child clade has greater growth rate, value will be positive.

    Pass "loky" to `parallel_backend` to use joblib with loky backend.

    Leaf nodes will have value NaN. If provided, any nodes not included in
    `work_mask` will also have value NaN.

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

    Saran NA, Nar F. 2025. Fast binary logistic regression. PeerJ Computer
        Science 11:e2579 https://doi.org/10.7717/peerj-cs.2579
    """

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if not alifestd_is_strictly_bifurcating_asexual(phylogeny_df):
        raise ValueError("phylogeny_df must be strictly bifurcating")

    if work_mask is not None:
        phylogeny_df[
            "alifestd_mark_clade_fblr_growth_children_asexual_mask"
        ] = work_mask

    if "origin_time" not in phylogeny_df.columns:
        raise ValueError("phylogeny_df must contain `origin_time` column")

    if "node_depth" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_node_depth_asexual(
            phylogeny_df, mutate=True
        )

    if "is_leaf" not in phylogeny_df.columns:
        phylogeny_df = alifestd_mark_leaves(phylogeny_df, mutate=True)

    inorder_traversal = alifestd_unfurl_traversal_inorder_asexual(
        phylogeny_df, mutate=True
    )

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.index = phylogeny_df["id"]

    if work_mask is not None:
        work_mask = phylogeny_df.loc[
            inorder_traversal,
            "alifestd_mark_clade_fblr_growth_children_asexual_mask",
        ].values

    leaves_mask = phylogeny_df.loc[inorder_traversal, "is_leaf"].values
    leaves = leaves_mask.copy()

    node_depths = phylogeny_df.loc[inorder_traversal, "node_depth"].values
    node_depths = node_depths.copy()  # contiguous for perf

    origin_times = phylogeny_df.loc[inorder_traversal, "origin_time"].values
    origin_times = origin_times.astype(float, copy=True)  # contiguous for perf

    n = len(node_depths)
    range_n = np.arange(n)
    lb_exclusive = _calc_boundaries(node_depths, range_n, default=-1)
    ub_exclusive = _calc_boundaries(node_depths, range_n[::-1], default=n)
    lb_inclusive = lb_exclusive + 1

    for arr in (leaves, node_depths, origin_times, ub_exclusive, lb_inclusive):
        arr.flags.writeable = False  # probably not needed?

    @(joblib.delayed if parallel_backend else lambda x: x)
    def fit_flbr_regression(target_idx: int) -> float:
        lb_inclusive_ = lb_inclusive[target_idx]
        ub_exclusive_ = ub_exclusive[target_idx]
        # leaf case should be masked out
        assert lb_inclusive_ < target_idx < ub_exclusive_ - 1

        descendant_slice = slice(lb_inclusive_, ub_exclusive_)
        sliced_target = target_idx - descendant_slice.start

        # predictor values; reshape to (N x 1) array for sklearn
        X = origin_times[descendant_slice].reshape(-1, 1)

        # sample weights; exclude target node and internal nodes
        assert leaves[target_idx] == 0.0
        w = leaves[descendant_slice]

        # classification target (response); 0 for left clade, 1 for right clade
        y = np.zeros(len(X), dtype=int)
        y[sliced_target:] = 1

        (res,) = fit_fblr(X_train=X[w], y_train=y[w])
        if np.isnan(res):
            warn_once("clade flbr growth regression produced NaN")
        return res

    sparse_mask = ~leaves_mask
    if work_mask is not None:
        sparse_mask &= work_mask

    results = np.full_like(node_depths, np.nan, dtype=float)
    if sparse_mask.any():
        sparse_operands = np.arange(len(node_depths))[sparse_mask]

        # use multiprocessing backend, although scikit suggests threading backend
        # see https://scikit-learn.org/stable/computing/parallelism.html#higher-level-parallelism-with-joblib
        context = (
            joblib.parallel_backend(parallel_backend, n_jobs=-1)
            if parallel_backend
            else contextlib.nullcontext()
        )
        with context:
            collect = (
                joblib.Parallel(batch_size=1000, n_jobs=-1)
                if parallel_backend
                else lambda x: np.fromiter(
                    x, dtype=float, count=len(sparse_operands)
                )
            )
            sparse_results = collect(
                map(fit_flbr_regression, progress_wrap(sparse_operands)),
            )

        results[sparse_mask] = sparse_results

    assert len(results) == len(node_depths)
    phylogeny_df["clade_fblr_growth_children"] = pd.Series(
        results, index=inorder_traversal, dtype=float
    )

    phylogeny_df.drop(
        columns=[
            "alifestd_mark_clade_fblr_growth_children_asexual_mask",
        ],
        errors="ignore",
        inplace=True,
    )

    return phylogeny_df
