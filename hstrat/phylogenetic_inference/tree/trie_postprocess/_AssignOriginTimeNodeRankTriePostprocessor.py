import copy

import anytree

from ...priors import ArbitraryPrior
from .._impl import TrieInnerNode, TrieLeafNode


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
    ) -> TrieInnerNode:
        """TODO

        Parameters
        ----------
            mutate : bool, default False
                Are side effects on the input argument `trie` allowed?
        """
        if not mutate:
            trie = copy.deepcopy(trie)

        for node in anytree.PreOrderIter(trie):
            setattr(node, self._assigned_property, node.rank)

        return trie
