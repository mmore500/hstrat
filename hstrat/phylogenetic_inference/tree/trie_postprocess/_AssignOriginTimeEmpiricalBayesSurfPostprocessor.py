import logging
import types
import typing
import warnings

import numpy as np
from phyloframe import legacy as pfl
import polars as pl

from ...._auxiliary_lib import (
    jit,
    jit_prange,
    log_context_duration,
    resolve_dstream_algo,
)
from ._AssignOriginTimeGeometricSurfPostprocessor import (
    _calc_geometric_origin_times,
)
from ._detail import TriePostprocessorBase
from ._detail._comparable_ranks import (
    get_sole_dstream_S,
    iter_retained_ranks,
    mark_inner_node_bounds,
)


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
    u1 = H - b + 1.0
    u2 = H - a + 1.0
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
        bounds = np.empty(num_retained + 3)
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


def _calc_posterior_origin_times(
    trie: pl.DataFrame,
    p_differentia_collision: float,
    dstream_algo: types.ModuleType,
    dstream_S: int,
    alphas: np.ndarray,
) -> np.ndarray:
    """Posterior mean origin times, relative to `dstream_S`, of all nodes
    (rows) for each prior exponent in `alphas` (columns).

    Leaves and unifurcating roots are assigned their rank. Trie must have
    contiguous ids, be topologically sorted, and provide an integer `rank`
    column, with leaf rank `dstream_T - 1`.
    """
    alphas = np.asarray(alphas, dtype=np.float64)
    if trie.is_empty():
        return np.zeros((0, len(alphas)))
    ranks, is_inner, compare_T, youngest_T = mark_inner_node_bounds(trie)
    inner_ranks = ranks[is_inner].astype(np.float64)
    youngest_T = youngest_T.astype(np.float64)

    inner_means = np.empty((len(compare_T), len(alphas)))
    with log_context_duration("_calc_posterior_means", logging.info):
        for chunk, retained in iter_retained_ranks(
            dstream_algo, dstream_S, compare_T
        ):
            inner_means[chunk] = _calc_posterior_means_fast_path(
                retained,
                inner_ranks[chunk],
                youngest_T[chunk],
                float(p_differentia_collision),
                int(dstream_S),
                alphas,
            )

    origin_times = np.repeat(
        (ranks - dstream_S).astype(np.float64)[:, None], len(alphas), axis=1
    )
    origin_times[is_inner] = inner_means
    return origin_times


def _calc_mrca_pair_counts(trie: pl.DataFrame) -> np.ndarray:
    """Number of leaf pairs whose most recent common ancestor is each node.

    Trie must have contiguous ids and be topologically sorted.
    """
    tree = trie.select(pl.col("id", "ancestor_id").cast(pl.Int64))
    num_leaves = pfl.alifestd_mark_to_array_polars(
        tree, pfl.alifestd_mark_num_leaves_polars
    ).astype(np.float64)
    ids = tree["id"].to_numpy()
    ancestors = tree["ancestor_id"].to_numpy()
    is_child = ids != ancestors
    child_sq_sums = np.zeros(len(ids))
    np.add.at(child_sq_sums, ancestors[is_child], num_leaves[is_child] ** 2)
    has_children = np.bincount(ancestors[is_child], minlength=len(ids)) > 0
    return np.where(has_children, (num_leaves**2 - child_sq_sums) / 2, 0.0)


def _benchmark(
    origin_times: np.ndarray,
    weights: np.ndarray,
    target: float,
    alpha_grid: np.ndarray,
) -> typing.Tuple[np.ndarray, float]:
    """Interpolate origin times between grid prior exponents bracketing
    where their weighted mean matches target.

    Posterior means are nondecreasing in prior exponent, so the weighted
    mean is monotonic over grid columns. Returns interpolated origin times
    and the corresponding interpolated prior exponent.
    """
    sums = weights @ origin_times
    if not sums[0] < target < sums[-1]:
        warnings.warn(
            f"benchmarking target {target} outside range attainable over "
            "alpha_grid; clamping prior exponent to grid end",
        )
    # fractional grid index where weighted mean matches target
    index = np.interp(target, sums, np.arange(len(alpha_grid)))
    k = min(int(index), len(alpha_grid) - 2)
    lam = index - k
    return (
        (1 - lam) * origin_times[:, k] + lam * origin_times[:, k + 1],
        float(np.interp(index, np.arange(len(alpha_grid)), alpha_grid)),
    )


def _call_polars(
    ftor: "AssignOriginTimeEmpiricalBayesSurfPostprocessor",
    trie: pl.DataFrame,
    p_differentia_collision: float,
) -> pl.DataFrame:
    """Implementation detail."""
    dstream_S = get_sole_dstream_S(trie)
    alphas = ftor._alpha_grid if ftor._alpha is None else [ftor._alpha]
    origin_times = _calc_posterior_origin_times(
        trie, p_differentia_collision, ftor._dstream_algo, dstream_S, alphas
    )
    weights = _calc_mrca_pair_counts(trie) if len(trie) else np.zeros(0)
    if ftor._alpha is None and weights.sum() > 0:
        target = np.dot(
            weights,
            _calc_geometric_origin_times(
                trie, p_differentia_collision, ftor._dstream_algo, dstream_S
            ),
        )
        origin_times, alpha = _benchmark(
            origin_times, weights, target, ftor._alpha_grid
        )
        logging.info(f" - empirical Bayes prior exponent: {alpha}")
    else:  # fixed prior exponent, or nothing to benchmark
        origin_times = origin_times[:, 0]
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

    A single tree-wide `alpha` is benchmarked (i.e., as in Bayesian
    benchmarking; Datta, Ghosh, et al. 2011), so that the average of node
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
        mutate: bool = False,
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
        progress_wrap : typing.Callable, optional
            Pass tqdm or equivalent to report progress.

            Not used in the current implementation.

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
        if not mutate:
            trie = trie.clone()
        return _call_polars(self, trie, p_differentia_collision)
