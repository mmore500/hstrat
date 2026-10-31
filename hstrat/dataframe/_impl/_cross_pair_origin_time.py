import logging
import typing

import numpy as np
import pandas as pd
from phyloframe import legacy as pfl
import polars as pl
import tqdm

from ..._auxiliary_lib import (
    log_context_duration,
    log_memory_usage,
    render_polars_snapshot,
)
from ...phylogenetic_inference.tree._impl import TrieInnerNode
from ...phylogenetic_inference.tree.trie_postprocess._detail import (
    TriePostprocessorBase,
)
from ._origin_time_cpp_impl_stub import cross_pair_sums, pool_inversions
from ._surface_explode_tips import SurfaceTips, tips_cpp_args

CROSS_PAIR_SUM = "hstrat_cross_pair_sum"
CROSS_PAIR_COUNT = "hstrat_cross_pair_count"


def attach_cross_pair_sums(
    trie: pl.DataFrame, tips: SurfaceTips
) -> pl.DataFrame:
    """Add per-node sums and counts of pairwise origin-time estimates over
    tip pairs that first split at each node.

    Must run on the raw trie from `surface_unpack_reconstruct`, before trunk
    deletion or collapsing, so that every tip is a leaf. Inner nodes other
    than branching nodes get zero sums and counts.
    """
    if not pfl.alifestd_has_contiguous_ids_polars(trie):
        raise NotImplementedError("non-contiguous ids not supported")
    if not pfl.alifestd_is_topologically_sorted_polars(trie):
        raise NotImplementedError("non-topologically-sorted not supported")
    logging.info("beginning attach_cross_pair_sums")
    with log_context_duration("tips.tip_of_node", logging.info):
        tip_of_node = tips.tip_of_node(trie["dstream_data_id"])
    with log_context_duration("cross_pair_sums", logging.info):
        sums, counts = cross_pair_sums(
            trie["ancestor_id"].cast(pl.Int64).to_numpy(),
            trie["dstream_rank"].cast(pl.Int64).to_numpy(),
            tip_of_node,
            *tips_cpp_args(tips),
            tqdm.tqdm,
        )
    log_memory_usage(logging.info)
    trie = trie.with_columns(
        pl.Series(CROSS_PAIR_SUM, sums, dtype=pl.Float64),
        pl.Series(CROSS_PAIR_COUNT, counts, dtype=pl.Int64),
    )
    render_polars_snapshot(trie, "with cross pair sums", logging.info)
    return trie


def _call_polars(
    ftor: "AssignOriginTimeCrossPairTriePostprocessor",
    trie: pl.DataFrame,
) -> pl.DataFrame:
    """Implementation detail."""
    if not pfl.alifestd_has_contiguous_ids_polars(trie):
        raise NotImplementedError("non-contiguous ids not supported")
    arrays = (
        trie.lazy()
        .select(
            pl.col("ancestor_id").cast(pl.Int64),
            pl.col("rank").cast(pl.Int64) - pl.col("dstream_S").cast(pl.Int64),
            pl.col(CROSS_PAIR_SUM).fill_null(0.0),
            pl.col(CROSS_PAIR_COUNT).fill_null(0),
        )
        .collect()
    )
    counts = arrays[CROSS_PAIR_COUNT].to_numpy().astype(np.float64)
    has_pairs = counts > 0
    # cross-pair mean at branching nodes; rank otherwise (e.g., leaves)
    times = np.where(
        has_pairs,
        arrays[CROSS_PAIR_SUM].to_numpy() / np.where(has_pairs, counts, 1),
        arrays["rank"].to_numpy(),
    ).astype(np.float64)
    if ftor._pool_inversions:
        with log_context_duration("pool_inversions", logging.info):
            times, num_merges = pool_inversions(
                arrays["ancestor_id"].to_numpy(), times, counts, tqdm.tqdm
            )
        logging.info(f" - {num_merges} inversion pooling merges")
    return trie.with_columns(
        pl.Series(ftor._assigned_property, times, dtype=pl.Float64),
    )


class AssignOriginTimeCrossPairTriePostprocessor(TriePostprocessorBase):
    """Functor to assign each trie node the mean of pairwise origin-time
    estimates over tip pairs that first split at that node.

    Requires `hstrat_cross_pair_sum` and `hstrat_cross_pair_count` columns,
    from `attach_cross_pair_sums` on the raw trie. Leaves and nodes without
    split pairs are assigned their rank, offset by `dstream_S`.

    If `pool_inversions`, inverted parent/child estimates are pooled to their
    pair-count-weighted mean, so ancestors are never assigned later times
    than their descendants. Pooling preserves the total of estimates over
    all tip pairs.
    """

    _assigned_property: str  # property name for assigned origin time
    _pool_inversions: bool  # pool inverted parent/child estimates?

    def __init__(
        self: "AssignOriginTimeCrossPairTriePostprocessor",
        assigned_property: str = "origin_time",
        *,
        pool_inversions: bool = True,
    ) -> None:
        """Initialize functor instance.

        Parameters
        ----------
        assigned_property : str, default "origin_time"
            Property name for assigned origin time.
        pool_inversions : bool, default True
            Pool inverted parent/child estimates?
        """
        self._assigned_property = assigned_property
        self._pool_inversions = pool_inversions

    def __call__(
        self: "AssignOriginTimeCrossPairTriePostprocessor",
        trie: typing.Union[TrieInnerNode, pd.DataFrame, pl.DataFrame],
        p_differentia_collision: float,
        mutate: bool = False,
        progress_wrap: typing.Callable = lambda x: x,
    ) -> typing.Union[TrieInnerNode, pd.DataFrame, pl.DataFrame]:
        """Assign origin times to trie nodes.

        Parameters
        ----------
        trie : pl.DataFrame
            The input trie to be postprocessed.

            Tries must have contiguous ids and provide `rank`, `dstream_S`,
            `hstrat_cross_pair_sum`, and `hstrat_cross_pair_count` columns.
        p_differentia_collision : float
            Probability of a randomly-generated differentia matching an
            existing differentia.

            Not used; already accounted for by cross-pair sums.
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
        if isinstance(trie, TrieInnerNode):
            raise NotImplementedError(
                "anytree tries are not supported; "
                "use dataframe tries (e.g., surface_postprocess_trie)",
            )
        elif isinstance(trie, pd.DataFrame):
            raise NotImplementedError(
                "pandas tries are not supported; use polars",
            )
        elif isinstance(trie, pl.DataFrame):
            if not mutate:
                trie = trie.clone()
            return _call_polars(self, trie)
        else:
            raise TypeError  # pragma: no cover
