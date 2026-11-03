import logging
import types
import typing
import warnings

import numpy as np
from phyloframe import legacy as pfl
import polars as pl

from ...._auxiliary_lib import (
    clamp,
    get_sole_scalar_value_polars,
    iter_dstream_ingest_times_sorted,
    jit,
    jit_prange,
    log_context_duration,
    resolve_dstream_algo,
    warn_experimental,
)
from ._AssignOriginTimeGeometricSurfPostprocessor import (
    _calc_geometric_chunk,
)
from ._detail import TriePostprocessorBase
from ._detail._comparable_ranks import mark_inner_node_bounds

# Prior exponents within this tolerance of 0, 1, or 2 use exact special-case
# closed forms. Near 1 and 2, the general formula loses precision to
# cancellation (dividing a small difference by `1 - alpha` or `2 - alpha`),
# while the special case's error grows with distance from the exponent. The
# square root of machine epsilon balances these, as is standard for such
# switchovers (e.g., finite-difference step sizes).
_SPECIAL_CASE_TOLERANCE = float(np.sqrt(np.finfo(np.float64).eps))


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
    # exact closed forms at alpha = 0 (uniform), and at alpha = 1 and 2, where
    # the general formula below divides by zero (see _SPECIAL_CASE_TOLERANCE)
    if abs(alpha) < _SPECIAL_CASE_TOLERANCE:
        mass = u2 - u1
        mean_u = (u1 + u2) / 2
    elif abs(alpha - 1) < _SPECIAL_CASE_TOLERANCE:
        mass = np.log(u2 / u1)
        mean_u = (u2 - u1) / mass
    elif abs(alpha - 2) < _SPECIAL_CASE_TOLERANCE:
        mass = 1 / u1 - 1 / u2
        mean_u = np.log(u2 / u1) / mass
    else:
        mass = (u2 ** (1 - alpha) - u1 ** (1 - alpha)) / (1 - alpha)
        moment = (u2 ** (2 - alpha) - u1 ** (2 - alpha)) / (2 - alpha)
        mean_u = moment / mass
    # clamp to interval's generations
    mean = clamp(H + 0.5 - mean_u, a, max(a, b - 1))
    if not np.isfinite(mean):
        # powers under/overflow only for extreme alpha (well beyond the
        # default grid); fall back to the uniform-prior interval mean
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
                # all intervals empty, i.e., node at the dstream_S boundary
                # with no generations to diverge over; take interval midpoint
                result[i, k] = (lo + hi - 1) / 2
    return result


def _calc_inner_estimates(
    trie: pl.DataFrame,
    p_differentia_collision: float,
    dstream_algo: types.ModuleType,
    dstream_S: int,
    alphas: np.ndarray,
    progress_wrap: typing.Callable,
) -> typing.Tuple[pl.DataFrame, np.ndarray]:
    """Posterior mean origin times of inner nodes for each prior exponent in
    `alphas`, and their geometric estimates, in one pass over comparable
    ranks.

    Returns a dataframe of all nodes' `base` origin time (i.e., rank,
    relative to `dstream_S`), `is_inner`, and `geometric` estimate (null for
    non-inner nodes), and a matrix of posterior means, with inner nodes as
    rows and prior exponents as columns.

    Trie must be non-empty, have contiguous ids, be topologically sorted,
    and provide an integer `rank` column, with leaf rank `dstream_T - 1`.
    """
    alphas = np.asarray(alphas, dtype=np.float64)
    bounds_df = mark_inner_node_bounds(trie_df=trie)
    inner_df = bounds_df.filter("is_inner")
    inner_ranks = inner_df["rank"].to_numpy().astype(np.float64)
    youngest_T = inner_df["clade_min_T"].to_numpy().astype(np.float64)
    p = float(p_differentia_collision)

    posterior = np.empty((len(inner_df), len(alphas)))
    geometric = np.empty(len(inner_df))
    with log_context_duration("_calc_inner_estimates", logging.info):
        for chunk, retained in progress_wrap(
            iter_dstream_ingest_times_sorted(
                dstream_algo=dstream_algo,
                dstream_S=dstream_S,
                T=inner_df["compare_T"].to_numpy(),
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
    assert np.isfinite(posterior).all()

    is_inner = bounds_df["is_inner"].to_numpy()
    all_geometric = np.full(len(bounds_df), np.nan)
    all_geometric[is_inner] = geometric
    estimates_df = bounds_df.select(
        base=(pl.col("rank") - dstream_S).cast(pl.Float64),
        is_inner="is_inner",
        geometric=pl.Series(all_geometric).fill_nan(None),
    )
    return estimates_df, posterior


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
    estimates_df, posterior = _calc_inner_estimates(
        trie=trie,
        p_differentia_collision=p_differentia_collision,
        dstream_algo=dstream_algo,
        dstream_S=dstream_S,
        alphas=alphas,
        progress_wrap=progress_wrap,
    )
    origin_times = np.repeat(
        estimates_df["base"].to_numpy()[:, None], len(alphas), axis=1
    )
    origin_times[estimates_df["is_inner"].to_numpy()] = posterior
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
    # posterior means are nondecreasing in prior exponent
    assert (np.diff(sums) >= -1e-6 * max(abs(sums[-1]), 1.0)).all()
    if target < sums[0] or target > sums[-1]:
        warnings.warn(
            f"benchmarking target {target} outside range attainable over "
            "alpha_grid; clamping prior exponent to nearest grid bound",
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
    if len(ftor._alpha_grid) == 1:  # fixed prior exponent
        alphas = ftor._alpha_grid
    elif pair_counts.sum() == 0:  # nothing to benchmark; uniform prior
        alphas = np.array([0.0])
    else:
        alphas = ftor._alpha_grid
    logging.info(f" - prior exponents evaluated: {len(alphas)}")

    estimates_df, posterior = _calc_inner_estimates(
        trie=trie,
        p_differentia_collision=p_differentia_collision,
        dstream_algo=ftor._dstream_algo,
        dstream_S=dstream_S,
        alphas=alphas,
        progress_wrap=progress_wrap,
    )
    is_inner = estimates_df["is_inner"].to_numpy()
    if len(alphas) == 1:
        inner_means, alpha = posterior[:, 0], float(alphas[0])
    else:
        weights = pair_counts[is_inner]
        geometric = estimates_df.filter("is_inner")["geometric"].to_numpy()
        assert len(weights) == len(geometric) == len(posterior)
        with log_context_duration(
            "_estimate_prior_exponent_by_benchmarking", logging.info
        ):
            inner_means, alpha = _estimate_prior_exponent_by_benchmarking(
                posterior=posterior,
                weights=weights,
                target=float(np.dot(weights, geometric)),
                alpha_grid=alphas,
            )
    logging.info(f" - empirical Bayes prior exponent: {alpha}")

    origin_times = estimates_df["base"].to_numpy().copy()
    origin_times[is_inner] = inner_means
    return trie.with_columns(
        pl.Series(ftor._assigned_property, origin_times, dtype=pl.Float64),
    )


@warn_experimental
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
    exponents bracketing the target. Alternately, pass a single-value
    `alpha_grid` to fix the prior exponent and skip benchmarking. So, the geometric estimator sets the tree-wide
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
    >>> hstrat.dataframe.surface_build_tree(
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
    _alpha_grid: np.ndarray  # prior exponents evaluated, or fixed exponent

    def __init__(
        self: "AssignOriginTimeEmpiricalBayesSurfPostprocessor",
        dstream_algo: typing.Union[str, types.ModuleType],
        assigned_property: str = "origin_time",
        *,
        alpha_grid: typing.Sequence[float] = tuple(np.linspace(-3, 3, 25)),
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
            attainable over the grid, estimates are clamped to the nearest
            grid bound, with a warning.

            A single value fixes the prior exponent, skipping benchmarking
            (e.g., `alpha_grid=[0]` gives the uniform prior).
        """
        alpha_grid = np.asarray(alpha_grid, dtype=np.float64)
        if (
            alpha_grid.ndim != 1
            or len(alpha_grid) == 0
            or not (np.diff(alpha_grid) > 0).all()
        ):
            raise ValueError("alpha_grid must be nonempty and increasing")
        self._dstream_algo = resolve_dstream_algo(dstream_algo)
        self._assigned_property = assigned_property
        self._alpha_grid = alpha_grid

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
