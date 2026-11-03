import logging
import types
import typing
import warnings

import numpy as np
from phyloframe import legacy as pfl
import polars as pl

from ...._auxiliary_lib import (
    get_sole_scalar_value_polars,
    iter_dstream_ingest_times_sorted,
    jit,
    jit_prange,
    log_context_duration,
    resolve_dstream_algo,
)
from ._AssignOriginTimeGeometricSurfPostprocessor import (
    _calc_geometric_chunk,
)
from ._detail import TriePostprocessorBase
from ._detail._comparable_ranks import mark_inner_node_bounds


@jit(nopython=True)
def _calc_prior_moments(
    a: float, b: float, H: float, alpha: float
) -> typing.Tuple[float, float]:
    """Prior mass and mean of divergence generation `t` within interval
    [`a`, `b`), for prior density proportional to `u ** -alpha` over
    backward lag `u = H - t + 1` from mismatch bound `H = max(hi, 1)`.

    Gives mass `b - a` and mean `(a + b - 1) / 2` for `alpha == 0`. Means
    are clipped to within the interval's generations.
    """
    if b <= a:
        return 0.0, (a + b - 1) / 2
    u1 = H - b + 1
    u2 = H - a + 1
    # exact closed forms, where the general case divides by zero (alpha = 1
    # or 2) or simplifies (alpha = 0); tolerance only selects the case
    if abs(alpha) < 1e-9:
        mass = u2 - u1
        mean_u = (u1 + u2) / 2
    elif abs(alpha - 1) < 1e-9:
        mass = np.log(u2 / u1)
        mean_u = (u2 - u1) / mass
    elif abs(alpha - 2) < 1e-9:
        mass = 1 / u1 - 1 / u2
        mean_u = np.log(u2 / u1) / mass
    else:
        mass = (u2 ** (1 - alpha) - u1 ** (1 - alpha)) / (1 - alpha)
        moment = (u2 ** (2 - alpha) - u1 ** (2 - alpha)) / (2 - alpha)
        mean_u = moment / mass
    mean = min(max(H + 0.5 - mean_u, a), max(a, b - 1))
    if not np.isfinite(mean):
        mean = (a + b - 1) / 2
    return mass, mean


@jit(nopython=True, parallel=True)
def _calc_posterior_means_fast_path(
    retained: np.ndarray,
    ranks: np.ndarray,
    youngest_T: np.ndarray,
    p: float,
    dstream_S: int,
    alphas: np.ndarray,
) -> np.ndarray:
    """Posterior mean divergence times, relative to `dstream_S`, of inner
    nodes (rows of sorted `retained`, ranks retained at their comparison
    `dstream_T`) for each prior exponent in `alphas` (columns)."""
    num_nodes, num_retained = retained.shape
    result = np.empty((num_nodes, len(alphas)))
    scratch = np.empty((num_nodes, num_retained + 3))  # per-node bounds
    for i in jit_prange(num_nodes):
        rank = ranks[i]
        # node's own interval: from node rank to first comparable rank
        # after (i.e., mismatch bound), or to youngest tip if none
        first_shared = youngest_T[i]
        for j in range(num_retained):
            if rank < retained[i, j] < youngest_T[i]:
                first_shared = retained[i, j]
                break
        lo = max(rank - dstream_S, 0.0)
        hi = max(first_shared - dstream_S, 0.0)
        H = max(hi, 1.0)

        # interval bounds: mismatch bound, node rank, then comparable ranks
        # before node rank, latest first, back to dstream_S
        bounds = scratch[i]
        bounds[0] = hi
        bounds[1] = lo
        num_bounds = 2
        for j in range(num_retained - 1, -1, -1):
            if retained[i, j] < rank:
                bounds[num_bounds] = max(retained[i, j] - dstream_S, 0.0)
                num_bounds += 1
        bounds[num_bounds] = 0.0
        num_bounds += 1

        for k in range(len(alphas)):
            numerator = 0.0
            denominator = 0.0
            p_collisions = 1.0  # jth interval requires j collisions
            for j in range(num_bounds - 1):
                mass, mean = _calc_prior_moments(
                    bounds[j + 1], bounds[j], H, alphas[k]
                )
                weight = mass * p_collisions
                numerator += weight * mean
                denominator += weight
                p_collisions *= p
            if denominator > 0:
                result[i, k] = numerator / denominator
            else:
                result[i, k] = (lo + hi - 1) / 2
    return result


class _InnerEstimates(typing.NamedTuple):
    """Origin time estimates, relative to `dstream_S`, of inner nodes."""

    base: np.ndarray  # all nodes' ranks, relative to `dstream_S`
    is_inner: np.ndarray  # is node inner?
    posterior: np.ndarray  # inner nodes (rows) by prior exponent (columns)
    geometric: np.ndarray  # geometric estimates of inner nodes


def _calc_inner_estimates(
    trie: pl.DataFrame,
    p_differentia_collision: float,
    dstream_algo: types.ModuleType,
    dstream_S: int,
    alphas: np.ndarray,
    progress_wrap: typing.Callable,
) -> _InnerEstimates:
    """Posterior mean origin times of inner nodes for each prior exponent in
    `alphas`, and their geometric estimates, in one pass over comparable
    ranks.

    Trie must be non-empty, have contiguous ids, be topologically sorted,
    and provide an integer `rank` column, with leaf rank `dstream_T - 1`.
    """
    alphas = np.asarray(alphas, dtype=np.float64)
    bounds = mark_inner_node_bounds(trie)
    inner = bounds.filter("is_inner")
    inner_ranks = inner["rank"].to_numpy().astype(np.float64)
    youngest_T = inner["clade_min_T"].to_numpy().astype(np.float64)
    p = float(p_differentia_collision)

    posterior = np.empty((len(inner), len(alphas)))
    geometric = np.empty(len(inner))
    with log_context_duration("_calc_inner_estimates", logging.info):
        for chunk, retained in progress_wrap(
            iter_dstream_ingest_times_sorted(
                dstream_algo,
                dstream_S,
                inner["compare_T"].to_numpy(),
                chunk_size=2**16,
            ),
        ):
            posterior[chunk] = _calc_posterior_means_fast_path(
                retained=retained,
                ranks=inner_ranks[chunk],
                youngest_T=youngest_T[chunk],
                p=p,
                dstream_S=int(dstream_S),
                alphas=alphas,
            )
            geometric[chunk] = _calc_geometric_chunk(
                retained=retained,
                ranks=inner_ranks[chunk],
                youngest_T=youngest_T[chunk],
                p=p,
                dstream_S=dstream_S,
            )

    base = (bounds["rank"].to_numpy() - dstream_S).astype(np.float64)
    return _InnerEstimates(
        base, bounds["is_inner"].to_numpy(), posterior, geometric
    )


def _calc_posterior_origin_times(
    trie: pl.DataFrame,
    p_differentia_collision: float,
    dstream_algo: types.ModuleType,
    dstream_S: int,
    alphas: np.ndarray,
    progress_wrap: typing.Callable,
) -> np.ndarray:
    """Posterior mean origin times, relative to `dstream_S`, of all nodes
    (rows) for each prior exponent in `alphas` (columns).

    Leaves and unifurcating roots are assigned their rank.
    """
    estimates = _calc_inner_estimates(
        trie,
        p_differentia_collision,
        dstream_algo,
        dstream_S,
        alphas,
        progress_wrap,
    )
    origin_times = np.repeat(estimates.base[:, None], len(alphas), axis=1)
    origin_times[estimates.is_inner] = estimates.posterior
    return origin_times


def _estimate_prior_exponent_by_benchmarking(
    posterior: np.ndarray,
    weights: np.ndarray,
    target: float,
    alpha_grid: np.ndarray,
) -> typing.Tuple[np.ndarray, float]:
    """Estimate the prior exponent (i.e., empirical Bayes hyperparameter)
    at which the weighted mean of posterior means matches the benchmark
    `target`, interpolating posterior means between bracketing grid
    exponents.

    Posterior means are nondecreasing in prior exponent, so the weighted
    mean is monotonic over grid columns. Returns interpolated means and the
    corresponding interpolated prior exponent.
    """
    sums = weights @ posterior
    if target < sums[0] or target > sums[-1]:
        warnings.warn(
            f"benchmarking target {target} outside range attainable over "
            "alpha_grid; clamping prior exponent to grid end",
        )
    # fractional grid index where weighted mean matches target
    index = np.interp(target, sums, np.arange(len(alpha_grid)))
    k = min(int(index), len(alpha_grid) - 2)
    lam = index - k
    return (
        (1 - lam) * posterior[:, k] + lam * posterior[:, k + 1],
        float(np.interp(index, np.arange(len(alpha_grid)), alpha_grid)),
    )


def _call_polars(
    ftor: "AssignOriginTimeEmpiricalBayesSurfPostprocessor",
    trie: pl.DataFrame,
    p_differentia_collision: float,
    progress_wrap: typing.Callable,
) -> pl.DataFrame:
    """Implementation detail."""
    if not pfl.alifestd_has_contiguous_ids_polars(trie):
        raise NotImplementedError("non-contiguous ids not supported")
    if not pfl.alifestd_is_topologically_sorted_polars(trie):
        raise NotImplementedError("non-topologically-sorted not supported")
    if trie.is_empty():
        return trie.with_columns(
            pl.Series(ftor._assigned_property, [], dtype=pl.Float64),
        )
    dstream_S = int(get_sole_scalar_value_polars(trie, "dstream_S"))

    with log_context_duration(
        "alifestd_mark_num_mrca_leaf_pairs_polars", logging.info
    ):
        pair_counts = pfl.alifestd_mark_to_array_polars(
            trie.select(pl.col("id", "ancestor_id").cast(pl.Int64)),
            pfl.alifestd_mark_num_mrca_leaf_pairs_polars,
        )
    if ftor._alpha is not None:  # fixed prior exponent
        alphas = [ftor._alpha]
    elif pair_counts.sum() == 0:  # nothing to benchmark; uniform prior
        alphas = [0.0]
    else:
        alphas = ftor._alpha_grid
    logging.info(f" - prior exponents evaluated: {len(alphas)}")

    estimates = _calc_inner_estimates(
        trie,
        p_differentia_collision,
        ftor._dstream_algo,
        dstream_S,
        alphas,
        progress_wrap,
    )
    if len(alphas) == 1:
        inner_means, alpha = estimates.posterior[:, 0], alphas[0]
    else:
        weights = pair_counts[estimates.is_inner]
        with log_context_duration(
            "_estimate_prior_exponent_by_benchmarking", logging.info
        ):
            inner_means, alpha = _estimate_prior_exponent_by_benchmarking(
                posterior=estimates.posterior,
                weights=weights,
                target=float(np.dot(weights, estimates.geometric)),
                alpha_grid=ftor._alpha_grid,
            )
    logging.info(f" - empirical Bayes prior exponent: {alpha}")

    origin_times = estimates.base.copy()
    origin_times[estimates.is_inner] = inner_means
    return trie.with_columns(
        pl.Series(ftor._assigned_property, origin_times, dtype=pl.Float64),
    )


class AssignOriginTimeEmpiricalBayesSurfPostprocessor(TriePostprocessorBase):
    """Functor to assign trie node origin times as posterior means, under a
    prior fit by empirical Bayes so that their tree-wide average matches
    the collision-unbiased geometric estimate (i.e., benchmarked Bayes).

    Spurious differentia collisions cause lineages to appear to share
    common ancestry for longer than they truly did. So, a node's children
    may truly have diverged not only within the node's own interval (i.e.,
    between its rank and its mismatch bound `hi`, the next comparable rank,
    where its children differ), but within any earlier interval between
    comparable ranks, back to `dstream_S`. Divergence within the jth
    interval before the node's own requires spurious collisions at j
    comparable ranks, with probability proportional to
    `p_differentia_collision ** j`.

    Each inner node is assigned its posterior mean divergence time `t`,
    under a power-law prior over backward lag from its mismatch bound,
    `u = max(hi, 1) - t + 1`, with density proportional to `u ** -alpha`.
    So, `u = 1` at the top of every node's own interval, whether its
    descendants were sampled long or soon after. With `alpha = 0`, the prior
    is uniform over generations. Higher `alpha` concentrates weight near the
    mismatch bound (i.e., more recent divergence), and lower `alpha` toward
    deeper intervals.

    A single tree-wide `alpha` is estimated by empirical Bayes (Casella
    1985), benchmarked (Datta et al. 2011) so that the average of node
    estimates, weighted by the number of leaf pairs whose most recent common
    ancestor each node is, matches that of
    `AssignOriginTimeGeometricSurfPostprocessor`, which is unbiased with
    respect to collisions without assuming a prior. Posterior means are
    evaluated over `alpha_grid` and linearly interpolated between the grid
    exponents bracketing the target. Alternately, pass a fixed `alpha` to
    skip benchmarking. So, the geometric estimator sets the tree-wide
    average over leaf pairs, and the posterior distributes it across nodes,
    with each estimate bounded within its own and earlier intervals.

    Comparable ranks are looked up as for
    `AssignOriginTimeGeometricSurfPostprocessor`: from `dstream_algo`, as
    the ranks retained at the largest of the node's children's minimum tip
    `dstream_T`, truncated at the clade's minimum tip `dstream_T`.

    References
    ----------
    Casella, G. (1985). An introduction to empirical Bayes data analysis.
    The American Statistician, 39(2), 83-87.
    https://doi.org/10.1080/00031305.1985.10479400

    Datta, G. S., Ghosh, M., Steorts, R., & Maples, J. (2011). Bayesian
    benchmarking with applications to small area estimation. TEST, 20(3),
    574-588. https://doi.org/10.1007/s11749-010-0218-y

    Notes
    -----
    Each node is estimated independently, so chronological consistency
    between nodes is not guaranteed.

    Only polars dataframe tries with a uniform `dstream_S` are supported
    (e.g., via `surface_postprocess_trie`). Origin times are relative to
    `dstream_S`. Leaf ranks are taken to be `dstream_T - 1`. Leaves and
    unifurcating roots are assigned their rank.

    Examples
    --------
    >>> hstrat.dataframe.surface_build_tree(  # doctest: +SKIP
    ...     df,
    ...     trie_postprocessor=(
    ...         hstrat.AssignOriginTimeEmpiricalBayesSurfPostprocessor(
    ...             "dstream.steady_algo",
    ...         )
    ...     ),
    ... )
    """

    _assigned_property: str  # property name for assigned origin time
    _dstream_algo: types.ModuleType  # downstream algorithm of surfaces
    _alpha_grid: np.ndarray  # prior exponents evaluated
    _alpha: typing.Optional[float]  # fixed prior exponent, if any

    def __init__(
        self: "AssignOriginTimeEmpiricalBayesSurfPostprocessor",
        dstream_algo: typing.Union[str, types.ModuleType],
        assigned_property: str = "origin_time",
        *,
        alpha_grid: typing.Sequence[float] = tuple(np.linspace(-3, 3, 25)),
        alpha: typing.Optional[float] = None,
    ) -> None:
        """Initialize functor instance.

        Parameters
        ----------
        dstream_algo : str or module
            Downstream algorithm used to curate surfaces, used to look up
            retained ranks.

            For example, `"dstream.steady_algo"` or `dstream.steady_algo`.
        assigned_property : str, default "origin_time"
            Property name for assigned origin time.
        alpha_grid : sequence of float, default 25 values from -3 to 3
            Prior exponents `alpha` evaluated, in increasing order.

            Heuristic. If the benchmarking target lies beyond the range
            attainable over the grid, estimates are clamped to the nearer
            end of the grid, with a warning. Ignored if `alpha` is given.
        alpha : float, optional
            Fixed prior exponent to use instead of benchmarking.

            For example, `alpha=0` gives the uniform prior. If given, the
            geometric benchmark is not computed.
        """
        alpha_grid = np.asarray(alpha_grid, dtype=np.float64)
        if len(alpha_grid) < 2 or not (np.diff(alpha_grid) > 0).all():
            raise ValueError("alpha_grid must be increasing, of length >= 2")
        self._dstream_algo = resolve_dstream_algo(dstream_algo)
        self._assigned_property = assigned_property
        self._alpha_grid = alpha_grid
        self._alpha = None if alpha is None else float(alpha)

    def __call__(
        self: "AssignOriginTimeEmpiricalBayesSurfPostprocessor",
        trie: pl.DataFrame,
        p_differentia_collision: float,
        mutate: bool = False,  # noqa: ARG002
        progress_wrap: typing.Callable = lambda x: x,
    ) -> pl.DataFrame:
        """Assign origin times to trie nodes.

        Parameters
        ----------
        trie : pl.DataFrame
            The input trie to be postprocessed.

            Only polars dataframe tries are supported; other types raise
            `NotImplementedError`. Tries must have contiguous ids, be
            topologically sorted, and provide `rank` and `dstream_S`
            columns.
        p_differentia_collision : float
            Probability of a randomly-generated differentia matching an
            existing differentia.
        mutate : bool, default False
            Are side effects on the input argument `trie` allowed?

            Not used, as polars operations don't modify their input.
        progress_wrap : typing.Callable, optional
            Pass tqdm or equivalent to report progress over chunks of
            inner nodes.

        Returns
        -------
        pl.DataFrame
            The postprocessed trie with assigned origin times.
        """
        if not isinstance(trie, pl.DataFrame):
            raise NotImplementedError(
                f"{type(trie)} tries are not supported; use polars "
                "dataframe tries (e.g., surface_postprocess_trie)",
            )
        return _call_polars(self, trie, p_differentia_collision, progress_wrap)
