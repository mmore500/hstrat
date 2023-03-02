import typing

import anytree
import numpy as np

from ._TrieInnerNode import TrieInnerNode
from ._assign_trie_origin_times_naive import assign_trie_origin_times_naive


def _calc_subtending_interval_means(
    trie: TrieInnerNode,
    prior: object,
) -> typing.Dict[int, float]:
    subtending_interval_means = dict()
    for node in anytree.PreOrderIter(trie):
        if node.is_leaf:
            pass
        elif node.parent is None:
            subtending_interval_means[id(node)] = 0
        else:
            subtending_interval_means[
                id(node)
            ] = prior.CalcIntervalConditionedMean(node.parent.rank, node.rank)
    return subtending_interval_means


def assign_trie_origin_times_unbiased(
    trie: TrieInnerNode,
    p_differentia_collision: float,
    prior: object,
) -> None:

    subtending_interval_means = _calc_subtending_interval_means(trie, prior)

    unbiased_subtending_expectations = dict()
    for node in anytree.PreOrderIter(trie):
        if node.is_leaf:
            pass
        elif node.parent is None:
            unbiased_subtending_expectations[id(node)] = 0
        else:
            unbiased_subtending_expectations[id(node)] = np.average(
                (
                    unbiased_subtending_expectations[id(node.parent)],
                    subtending_interval_means[id(node)],
                ),
                weights=(
                    p_differentia_collision
                    * prior.CalcIntervalProbabilityProxy(0, node.parent.rank),
                    1.0
                    * prior.CalcIntervalProbabilityProxy(
                        node.parent.rank, node.rank
                    ),
                )
                if node.parent.rank != node.rank
                else (1, 1),
            )

    for node in anytree.PreOrderIter(trie):
        if node.is_leaf:
            node.origin_time = node.rank + 0.5
        elif node.parent is None:
            node.origin_time = 0
        else:
            node.origin_time = np.average(
                (
                    unbiased_subtending_expectations[id(node)],
                    prior.CalcIntervalConditionedMean(
                        node.rank,
                        min(child.rank for child in node.children) - 1,
                    ),
                ),
                weights=(p_differentia_collision, 1.0),
            )
