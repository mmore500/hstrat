import typing

from ...._auxiliary_lib import (
    AnyTreeFastPreOrderIter,
    anytree_iterative_deepcopy,
)
from .._impl import TrieInnerNode


class AssignOriginTimeNodeRankTriePostprocessor:

    _assigned_property: str

    def __init__(
        self: "AssignOriginTimeNodeRankTriePostprocessor",
        assigned_property: str = "origin_time",
    ) -> None:
        self._assigned_property = assigned_property

    def __call__(
        self: "AssignOriginTimeNodeRankTriePostprocessor",
        trie: TrieInnerNode,
        p_differentia_collision: float,
        mutate: bool = False,
        progress_wrap: typing.Callable = lambda x: x,
    ) -> TrieInnerNode:
        """TODO

        Parameters
        ----------
            mutate : bool, default False
                Are side effects on the input argument `trie` allowed?

        Returns
        -------
        TrieInnerNode
            The postprocessed trie.
        """
        if not mutate:
            trie = anytree_iterative_deepcopy(
                trie, progress_wrap=progress_wrap
            )

        for node in progress_wrap(AnyTreeFastPreOrderIter(trie)):
            setattr(node, self._assigned_property, node.rank)

        return trie
