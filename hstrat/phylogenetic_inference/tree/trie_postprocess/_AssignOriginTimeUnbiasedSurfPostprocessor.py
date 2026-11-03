import logging
import types
import typing

import numpy as np
from phyloframe import legacy as pfl
import polars as pl

from ...._auxiliary_lib import (
    find_first_between_sorted_rows,
    get_sole_scalar_value_polars,
    iter_dstream_ingest_times_sorted,
    log_context_duration,
    warn_experimental,
)
from ._detail import TriePostprocessorBase
from ._detail._comparable_ranks import (
    get_dstream_algo,
    mark_inner_node_bounds,
)


def _calc_unbiased_chunk(
    retained_ranks: np.ndarray,
    ranks: np.ndarray,
    clade_min_T: np.ndarray,
    p: float,
    dstream_S: int,
) -> np.ndarray:
    """Unbiased origin time estimates, relative to `dstream_S`, for a chunk
    of inner nodes, given sorted `retained_ranks` at their comparison
    `dstream_T`."""
    # mismatch rank: first comparable rank after node; and following
    # comparable rank, bounding the next interval; ranks at or after the
    # clade's youngest tip are not comparable
    first_shared, second_shared = find_first_between_sorted_rows(
        rows=retained_ranks, after=ranks, before=clade_min_T, num=2
    ).T

    # intervals end at youngest tip if no further comparable rank
    is_terminal = ~np.isfinite(first_shared)
    first_shared = np.where(is_terminal, clade_min_T, first_shared)
    second_shared = np.where(
        np.isfinite(second_shared), second_shared, clade_min_T
    )

    # midpoints of node's interval and the next, relative to dstream_S;
    # divergence cannot precede dstream_S
    lo = np.clip(ranks - dstream_S, 0, None)
    mid = np.clip(first_shared - dstream_S, 0, None)
    hi = np.clip(second_shared - dstream_S, 0, None)
    this_midpoints = (lo + mid - 1) / 2
    next_midpoints = (mid + hi - 1) / 2

    # spurious collisions at successive comparable ranks are geometric, so
    # extrapolating back from next interval cancels expected inflation;
    # no extrapolation if no comparable rank remains to collide at
    return np.where(
        is_terminal,
        this_midpoints,
        (this_midpoints - p * next_midpoints) / (1 - p),
    )


def _calc_unbiased_origin_times(
    trie: pl.DataFrame,
    p_differentia_collision: float,
    dstream_algo: types.ModuleType,
    dstream_S: int,
    progress_wrap: typing.Callable,
) -> np.ndarray:
    """Calculate origin times, relative to `dstream_S`, that are unbiased
    with respect to spurious differentia collisions.

    Trie must be non-empty, have contiguous ids, be topologically sorted,
    and provide an integer `rank` column, with leaf rank `dstream_T - 1`.
    """
    bounds_df = mark_inner_node_bounds(trie_df=trie)
    is_inner = (~bounds_df["is_leaf"] & ~bounds_df["is_root"]).to_numpy()
    inner_df = bounds_df.filter(is_inner)
    inner_ranks = inner_df["rank"].to_numpy().astype(np.float64)
    clade_min_T = inner_df["clade_min_T"].to_numpy().astype(np.float64)

    inner_times = np.empty(len(inner_df))
    with log_context_duration("_calc_unbiased_chunk", logging.info):
        for chunk, retained_ranks in iter_dstream_ingest_times_sorted(
            dstream_algo=dstream_algo,
            dstream_S=dstream_S,
            T=inner_df["compare_T"].to_numpy(),
            chunk_size=2**16,
            progress_wrap=progress_wrap,
        ):
            inner_times[chunk] = _calc_unbiased_chunk(
                retained_ranks=retained_ranks,
                ranks=inner_ranks[chunk],
                clade_min_T=clade_min_T[chunk],
                p=p_differentia_collision,
                dstream_S=dstream_S,
            )

    assert np.isfinite(inner_times).all()

    origin_times = (bounds_df["rank"].to_numpy() - dstream_S).astype(
        np.float64
    )
    origin_times[is_inner] = inner_times
    return origin_times


def _call_polars(
    ftor: "AssignOriginTimeUnbiasedSurfPostprocessor",
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

    origin_times = _calc_unbiased_origin_times(
        trie=trie,
        p_differentia_collision=p_differentia_collision,
        dstream_algo=get_dstream_algo(trie),
        dstream_S=int(get_sole_scalar_value_polars(trie, "dstream_S")),
        progress_wrap=progress_wrap,
    )
    return trie.with_columns(
        pl.Series(ftor._assigned_property, origin_times, dtype=pl.Float64),
    )


@warn_experimental
class AssignOriginTimeUnbiasedSurfPostprocessor(TriePostprocessorBase):
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

    Comparable ranks for a node are looked up, via the trie's uniform
    `dstream_algo` column (as attached by `surface_unpack_reconstruct`), as
    the ranks retained at the largest of its children's minimum tip
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
    roots are assigned their rank.

    Examples
    --------
    Pass as `trie_postprocessor` to `hstrat.dataframe.surface_build_tree`
    or `hstrat.dataframe.surface_postprocess_trie`, e.g.,

    >>> hstrat.dataframe.surface_build_tree(
    ...     df,
    ...     trie_postprocessor=(
    ...         hstrat.AssignOriginTimeUnbiasedSurfPostprocessor()
    ...     ),
    ... )

    or, from the command line,
    `--trie-postprocessor 'hstrat.AssignOriginTimeUnbiasedSurfPostprocessor()'`.
    """

    _assigned_property: str  # property name for assigned origin time

    def __init__(
        self: "AssignOriginTimeUnbiasedSurfPostprocessor",
        assigned_property: str = "origin_time",
    ) -> None:
        """Initialize functor instance.

        Parameters
        ----------
        assigned_property : str, default "origin_time"
            Property name for assigned origin time.
        """
        self._assigned_property = assigned_property

    def __call__(
        self: "AssignOriginTimeUnbiasedSurfPostprocessor",
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
