import logging
import types
import typing

import numpy as np
import polars as pl

from ...._auxiliary_lib import log_context_duration, resolve_dstream_algo
from ._detail import TriePostprocessorBase
from ._detail._comparable_ranks import (
    first_retained_between,
    get_sole_dstream_S,
    iter_retained_ranks,
    mark_inner_node_bounds,
)


def _calc_geometric_origin_times(
    trie: pl.DataFrame,
    p_differentia_collision: float,
    dstream_algo: types.ModuleType,
    dstream_S: int,
) -> np.ndarray:
    """Calculate origin times, relative to `dstream_S`, that are unbiased
    with respect to spurious differentia collisions.

    Trie must have contiguous ids, be topologically sorted, and provide an
    integer `rank` column, with leaf rank `dstream_T - 1`.
    """
    p = p_differentia_collision
    if trie.is_empty():
        return np.zeros(0, dtype=np.float64)
    ranks, is_inner, compare_T, youngest_T = mark_inner_node_bounds(trie)

    # mismatch rank: first comparable rank after node; and following
    # comparable rank, bounding the next interval; ranks at or after the
    # clade's youngest tip are not comparable
    shared = np.full((len(compare_T), 2), np.inf)
    with log_context_duration("first_retained_between", logging.info):
        for chunk, retained in iter_retained_ranks(
            dstream_algo, dstream_S, compare_T
        ):
            shared[chunk] = first_retained_between(
                retained,
                ranks[is_inner][chunk].astype(np.float64),
                youngest_T[chunk].astype(np.float64),
                num=2,
            )
    first_shared, second_shared = shared.T

    # intervals end at youngest tip if no further comparable rank
    youngest_T = youngest_T.astype(np.float64)
    is_terminal = ~np.isfinite(first_shared)
    first_shared = np.where(is_terminal, youngest_T, first_shared)
    second_shared = np.where(
        np.isfinite(second_shared), second_shared, youngest_T
    )

    # midpoints of node's interval and the next, relative to dstream_S;
    # divergence cannot precede dstream_S
    lo = np.maximum(ranks[is_inner] - dstream_S, 0)
    mid = np.maximum(first_shared - dstream_S, 0)
    hi = np.maximum(second_shared - dstream_S, 0)
    this_midpoints = (lo + mid - 1) / 2
    next_midpoints = (mid + hi - 1) / 2

    # spurious collisions at successive comparable ranks are geometric, so
    # extrapolating back from next interval cancels expected inflation;
    # no extrapolation if no comparable rank remains to collide at
    origin_times = (ranks - dstream_S).astype(np.float64)
    origin_times[is_inner] = np.where(
        is_terminal,
        this_midpoints,
        (this_midpoints - p * next_midpoints) / (1 - p),
    )
    return origin_times


def _call_polars(
    ftor: "AssignOriginTimeGeometricSurfPostprocessor",
    trie: pl.DataFrame,
    p_differentia_collision: float,
) -> pl.DataFrame:
    """Implementation detail."""
    origin_times = _calc_geometric_origin_times(
        trie,
        p_differentia_collision,
        ftor._dstream_algo,
        get_sole_dstream_S(trie),
    )
    return trie.with_columns(
        pl.Series(ftor._assigned_property, origin_times, dtype=pl.Float64),
    )


class AssignOriginTimeGeometricSurfPostprocessor(TriePostprocessorBase):
    """Functor to scale back trie node origin times so that their expected
    values under spurious differentia collisions are unbiased.

    Spurious collisions cause lineages to appear to share common ancestry
    for longer than they truly did, so naive origin-time estimates (i.e.,
    MRCA generations) are biased toward being too recent. For a pair of
    lineages that truly diverged within some interval between comparable
    retained ranks, the number of subsequent comparable ranks with spurious
    collisions is geometrically distributed. Each inner node is assigned

        (c0 - p * c1) / (1 - p),

    where c0 is the midpoint of the interval between the node's rank and the
    next comparable rank (i.e., where its children differ), c1 is the
    midpoint of the following comparable interval, and p is
    `p_differentia_collision`. The expected value of this estimate, over
    collision outcomes, telescopes to the collision-free interval midpoint
    for every true divergence time. Where no comparable rank remains between
    a node and its youngest tip, the interval midpoint is assigned as-is.

    Comparable ranks for a node are looked up from `dstream_algo`, as the
    ranks retained at the largest of its children's minimum tip
    `dstream_T` (i.e., ranks retained by every child's youngest tip),
    truncated at the clade's minimum tip `dstream_T`.

    Estimates are unbiased on average, not individually: they may precede
    ancestors' estimates, giving negative branch lengths. Topology is left
    unchanged. For individual estimates bounded within their own and earlier
    intervals, see `AssignOriginTimeEmpiricalBayesSurfPostprocessor`.

    Notes
    -----

    Only polars dataframe tries with a uniform `dstream_S` are supported
    (e.g., via `surface_postprocess_trie`). Origin times are relative to
    `dstream_S`. Leaf ranks are taken to be `dstream_T - 1`. Leaves and
    unifurcating roots are assigned their rank.

    Examples
    --------
    Pass as `trie_postprocessor` to `hstrat.dataframe.surface_build_tree`
    or `hstrat.dataframe.surface_postprocess_trie`, e.g.,

    >>> hstrat.dataframe.surface_build_tree(  # doctest: +SKIP
    ...     df,
    ...     trie_postprocessor=(
    ...         hstrat.AssignOriginTimeGeometricSurfPostprocessor(
    ...             "dstream.steady_algo",
    ...         )
    ...     ),
    ... )

    or, from the command line,
    `--trie-postprocessor 'hstrat.AssignOriginTimeGeometricSurfPostprocessor("dstream.steady_algo")'`.
    """

    _assigned_property: str  # property name for assigned origin time
    _dstream_algo: types.ModuleType  # downstream algorithm of surfaces

    def __init__(
        self: "AssignOriginTimeGeometricSurfPostprocessor",
        dstream_algo: typing.Union[str, types.ModuleType],
        assigned_property: str = "origin_time",
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
        """
        self._dstream_algo = resolve_dstream_algo(dstream_algo)
        self._assigned_property = assigned_property

    def __call__(
        self: "AssignOriginTimeGeometricSurfPostprocessor",
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
