import math
import typing

import pandas as pd
import polars as pl

from ...._auxiliary_lib import (
    AnyTreeFastPreOrderIter,
    anytree_iterative_deepcopy,
)
from .._impl import TrieInnerNode, TrieLeafNode
from ._detail import TriePostprocessorBase


def _call_anytree(
    ftor: "AssignDestructionTimeYoungestPlusOneTriePostprocessor",
    trie: TrieInnerNode,
    progress_wrap: typing.Callable = lambda x: x,
) -> TrieInnerNode:
    """Implementation detail."""
    for node in progress_wrap(AnyTreeFastPreOrderIter(trie)):
        if node.is_leaf:
            setattr(node, ftor._assigned_property, math.inf)
            assert isinstance(node, TrieLeafNode)
        else:
            destruction_time = (
                min(
                    getattr(child, ftor._origin_time_property)
                    for child in node.children
                )
                + 1
            )
            setattr(node, ftor._assigned_property, destruction_time)

        assert hasattr(node, ftor._assigned_property)

    return trie


class AssignDestructionTimeYoungestPlusOneTriePostprocessor(
    TriePostprocessorBase,
):
    """Functor to assign a destruction time property to trie nodes.

    Destruction time of leaf nodes are set to infinity. Destruction time of
    inner nodes is calculated as the minimum of its children's origin times
    plus one.
    """

    _assigned_property: str  # property name for the assigned destruction time.
    _origin_time_property: str  # property name for the node's origin time.

    def __init__(
        self: "AssignDestructionTimeYoungestPlusOneTriePostprocessor",
        assigned_property: str = "destruction_time",
        origin_time_property: str = "origin_time",
    ) -> None:
        """Initialize functor instance.

        Parameters
        ----------
        assigned_property : str, default "destruction_time"
            The property name for the assigned destruction tim.
        origin_time_property : str, default "origin_time"
            The property name for the node's origin time.
        """
        self._assigned_property = assigned_property
        self._origin_time_property = origin_time_property

    def __call__(
        self: "AssignDestructionTimeYoungestPlusOneTriePostprocessor",
        trie: TrieInnerNode,
        p_differentia_collision: float,
        mutate: bool = False,
        progress_wrap: typing.Callable = lambda x: x,
    ) -> TrieInnerNode:
        """Assign destruction times to trie nodes based on their childrens'
        origin times.

        Parameters
        ----------
        trie : TrieInnerNode
            The input trie to be postprocessed.
        p_differentia_collision : float
            The multiplicative inverse of the number of possible
            differentia.

            Not used in the current implementation.
        mutate : bool, default False
            Are side effects on the input argument `trie` allowed?
        progress_wrap : typing.Callable, optional
            Pass tqdm or equivalent to report progress.

        Returns
        -------
        TrieInnerNode
            The postprocessed trie with assigned destruction times.
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
        elif isinstance(trie, (pl.DataFrame, pd.DataFrame)):
            raise NotImplementedError  # pragma: no cover
        else:
            raise TypeError  # pragma: no cover
