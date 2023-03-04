import anytree
import numpy as np

from ...priors import ArbitraryPrior

from ._TrieInnerNode import TrieInnerNode
from ._TrieLeafNode import TrieLeafNode


def assign_trie_origin_times_naive(
    trie: TrieInnerNode,
    assigned_property: str = "origin_time",
    prior: object = ArbitraryPrior(),  # ok --- ArbitraryPrior is immutable
) -> None:
    for node in anytree.PreOrderIter(trie):
        if node.is_leaf:
            setattr(node, assigned_property, node.rank)
            assert isinstance(node, TrieLeafNode)
        elif node.parent is None:
            setattr(node, assigned_property, 0)
        else:
            setattr(
                node,
                assigned_property,
                prior.CalcIntervalConditionedMean(
                    node.rank,
                    min(
                        (
                            child.rank
                            for child in node.children
                            if not child.is_leaf
                        ),
                        default=node.rank + 1,
                    ),
                ),
            )
