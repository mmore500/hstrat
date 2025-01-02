import typing

import pandas as pd
import polars as pl

from ...._auxiliary_lib import (
    AnyTreeFastPreOrderIter,
    anytree_iterative_deepcopy,
)
from .._impl import TrieInnerNode
from ._detail import TriePostprocessorBase


def _call_anytree(
    ftor: "AssignOriginTimeNodeRankTriePostprocessor",
    trie: TrieInnerNode,
    progress_wrap: typing.Callable,
) -> TrieInnerNode:
    for node in progress_wrap(AnyTreeFastPreOrderIter(trie)):
        t0 = getattr(node, ftor._t0) if isinstance(ftor._t0, str) else ftor._t0
        setattr(node, ftor._assigned_property, node.rank - t0)

    return trie


def _call_pandas(
    ftor: "AssignOriginTimeNodeRankTriePostprocessor",
    trie: pd.DataFrame,
) -> TrieInnerNode:
    t0 = trie[ftor._t0] if isinstance(ftor._t0, str) else ftor._t0
    trie[ftor._assigned_property] = trie["rank"] - t0
    return trie


def _call_polars(
    ftor: "AssignOriginTimeNodeRankTriePostprocessor",
    trie: pl.DataFrame,
) -> TrieInnerNode:
    t0 = pl.col(ftor._t0) if isinstance(ftor._t0, str) else pl.lit(ftor._t0)
    return trie.with_columns(
        (pl.col("rank") - t0).alias(ftor._assigned_property),
    )


class AssignOriginTimeNodeRankTriePostprocessor(TriePostprocessorBase):
    """Functor to assign trie nodes' rank as their the origin time."""

    _assigned_property: str
    _t0: int

    def __init__(
        self: "AssignOriginTimeNodeRankTriePostprocessor",
        assigned_property: str = "origin_time",
        *,
        t0: typing.Union[int, str] = 0,
    ) -> None:
        """Initialize functor instance.

        Parameters
        ----------
        assigned_property : str, default "origin_time"
            The property name for the assigned origin time.
        t0 : int or str, default 0
            The property name or constant value for the origin time offset.
        """
        self._assigned_property = assigned_property
        self._t0 = t0

    def __call__(
        self: "AssignOriginTimeNodeRankTriePostprocessor",
        trie: TrieInnerNode,
        p_differentia_collision: float,
        mutate: bool = False,
        progress_wrap: typing.Callable = lambda x: x,
    ) -> TrieInnerNode:
        """Assign origin times to trie nodes.

        Parameters
        ----------
        trie : TrieInnerNode
            The input trie to be postprocessed.
        p_differentia_collision : float
            Probability of a randomly-generated differentia matching an
            existing differentia.
            Not used in the current implementation.
        mutate : bool, default False
            Are side effects on the input argument `trie` allowed?
        progress_wrap : typing.Callable, optional
            Pass tqdm or equivalent to report progress.

        Returns
        -------
        TrieInnerNode
            The postprocessed trie with assigned origin times.
        """
        if isinstance(trie, TrieInnerNode):
            if not mutate:
                trie = anytree_iterative_deepcopy(
                    trie, progress_wrap=progress_wrap
                )
            return _call_anytree(
                self,
                trie,
                progress_wrap=progress_wrap,
            )
        elif isinstance(trie, pd.DataFrame):
            if not mutate:
                trie = trie.copy()
            return _call_pandas(
                self,
                trie,
            )  # no progress wrap
        elif isinstance(trie, pl.DataFrame):
            if not mutate:
                trie = trie.clone()
            return _call_polars(
                self,
                trie,
            )  # no progress wrap
        else:
            raise TypeError  # pragma: no cover
