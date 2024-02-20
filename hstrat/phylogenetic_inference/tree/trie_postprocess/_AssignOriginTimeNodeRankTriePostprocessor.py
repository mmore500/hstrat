import typing

from ...._auxiliary_lib import (
    AnyTreeFastPreOrderIter,
    anytree_iterative_deepcopy,
)
from .._impl import TrieInnerNode
from ._detail import TriePostprocessorBase


class AssignOriginTimeNodeRankTriePostprocessor(TriePostprocessorBase):
    """Functor to assign trie nodes' rank as their the origin time."""

    _assigned_property: str

    def __init__(
        self: "AssignOriginTimeNodeRankTriePostprocessor",
        assigned_property: str = "origin_time",
    ) -> None:
        """Initialize functor instance.

        Parameters
        ----------
        assigned_property : str, default "origin_time"
            The property name for the assigned origin time.
        """
        self._assigned_property = assigned_property

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
        if not mutate:
            trie = anytree_iterative_deepcopy(
                trie, progress_wrap=progress_wrap
            )

        for node in progress_wrap(AnyTreeFastPreOrderIter(trie)):
            setattr(node, self._assigned_property, node.rank)

        return trie
