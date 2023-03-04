import copy

import anytree

from ...priors import ArbitraryPrior
from .._impl import TrieInnerNode, TrieLeafNode


class AssignOriginTimeNaiveTriePostprocessor:

    _assigned_property: str
    _prior: object

    def __init__(
        self: "AssignOriginTimeNaiveTriePostprocessor",
        prior: object = ArbitraryPrior(),  # ok as kwarg; immutable
        assigned_property: str = "origin_time",
    ) -> None:
        self._assigned_property = assigned_property
        self._prior = prior

    def __call__(
        self: "AssignOriginTimeNaiveTriePostprocessor",
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
            if node.is_leaf:
                setattr(node, self._assigned_property, node.rank)
                assert isinstance(node, TrieLeafNode)
            elif node.parent is None:
                setattr(node, self._assigned_property, 0)
            else:
                interval_mean = self._prior.CalcIntervalConditionedMean(
                    node.rank,
                    min(
                        (
                            child.rank
                            for child in node.children
                            if not child.is_leaf
                        ),
                        default=node.rank + 1,
                    ),
                )
                setattr(
                    node,
                    self._assigned_property,
                    min(
                        interval_mean,
                        min(
                            (leaf.rank for leaf in node.leaves),
                            default=interval_mean,
                        ),
                    ),
                )

            assert hasattr(node, self._assigned_property)

        return trie
