import copy

import anytree
import numpy as np

from ...priors import ArbitraryPrior
from .._impl import TrieInnerNode, TrieLeafNode


def assign_trie_origin_times_naive(
    trie: TrieInnerNode,
    assigned_property: str = "origin_time",
    prior: object = ArbitraryPrior(),  # ok --- ArbitraryPrior is immutable
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
            setattr(node, assigned_property, node.rank)
            assert isinstance(node, TrieLeafNode)
        elif node.parent is None:
            setattr(node, assigned_property, 0)
        else:
            interval_mean = prior.CalcIntervalConditionedMean(
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
                assigned_property,
                min(
                    interval_mean,
                    min(
                    (leaf.rank for leaf in node.leaves), default=interval_mean,),
                ),
            )

        assert hasattr(node, assigned_property)

    return trie
