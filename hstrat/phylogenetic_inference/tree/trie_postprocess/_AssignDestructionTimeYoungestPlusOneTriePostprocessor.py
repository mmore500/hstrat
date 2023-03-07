import math
import typing

from ...._auxiliary_lib import (
    AnyTreeFastPreOrderIter,
    anytree_iterative_deepcopy,
)
from .._impl import TrieInnerNode, TrieLeafNode


class AssignDestructionTimeYoungestPlusOneTriePostprocessor:

    _assigned_property: str
    _origin_time_property: str

    def __init__(
        self: "AssignDestructionTimeYoungestPlusOneTriePostprocessor",
        assigned_property: str = "destruction_time",
        origin_time_property: str = "origin_time",
    ) -> None:
        self._assigned_property = assigned_property
        self._origin_time_property = origin_time_property

    def __call__(
        self: "AssignDestructionTimeYoungestPlusOneTriePostprocessor",
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
            if node.is_leaf:
                setattr(node, self._assigned_property, math.inf)
                assert isinstance(node, TrieLeafNode)
            else:
                destruction_time = (
                    min(
                        getattr(child, self._origin_time_property)
                        for child in node.children
                    )
                    + 1
                )
                setattr(node, self._assigned_property, destruction_time)

            assert hasattr(node, self._assigned_property)

        return trie
