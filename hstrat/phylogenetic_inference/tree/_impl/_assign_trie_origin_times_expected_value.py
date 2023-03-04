import typing

import anytree
import numpy as np

from ._TrieInnerNode import TrieInnerNode
from ._TrieLeafNode import TrieLeafNode
from ._assign_trie_origin_times_naive import assign_trie_origin_times_naive


def assign_trie_origin_times_expected_value(
    trie: TrieInnerNode,
    p_differentia_collision: float,
    prior: object,
    assigned_property: str = "origin_time",
) -> None:

    assign_trie_origin_times_naive(trie, "_naive_origin_time", prior)

    for node in anytree.PreOrderIter(trie):
        if node.is_leaf:
            setattr(node, assigned_property, node.rank)
            assert isinstance(node, TrieLeafNode)
        elif node.parent is None:
            setattr(node, assigned_property, 0)
        else:
            assert node.children
            weights = (
                p_differentia_collision,
                1
                * prior.CalcIntervalProbabilityProxy(
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
            values = (
                getattr(node.parent, assigned_property),
                node._naive_origin_time,
            )
            collision_corrected_origin_time = np.average(
                values,
                weights=weights,
            )
            print(values, weights, collision_corrected_origin_time)
            setattr(node, assigned_property, collision_corrected_origin_time)
