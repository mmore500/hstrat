import typing

import numpy as np

from ...._auxiliary_lib import (
    AnyTreeFastPreOrderIter,
    anytree_iterative_deepcopy,
)
from .._impl import TrieInnerNode, TrieLeafNode
from ._AssignOriginTimeNaiveTriePostprocessor import (
    AssignOriginTimeNaiveTriePostprocessor,
)


class AssignOriginTimeExpectedValueTriePostprocessor:

    _assigned_property: str
    _prior: object

    def __init__(
        self: "AssignOriginTimeExpectedValueTriePostprocessor",
        prior: object,
        assigned_property: str = "origin_time",
    ) -> None:
        self._assigned_property = assigned_property
        self._prior = prior

    def __call__(
        self: "AssignOriginTimeExpectedValueTriePostprocessor",
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

        trie = AssignOriginTimeNaiveTriePostprocessor(
            prior=self._prior, assigned_property="_naive_origin_time"
        )(
            trie,
            p_differentia_collision=p_differentia_collision,
            mutate=True,
            progress_wrap=progress_wrap,
        )

        for node in progress_wrap(AnyTreeFastPreOrderIter(trie)):
            if node.is_leaf:
                setattr(node, self._assigned_property, node.rank)
                assert isinstance(node, TrieLeafNode)
            elif node.parent is None:
                setattr(node, self._assigned_property, 0)
            else:
                assert node.children
                weights = (
                    p_differentia_collision,
                    1
                    * self._prior.CalcIntervalProbabilityProxy(
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
                    getattr(node.parent, self._assigned_property),
                    node._naive_origin_time,
                )
                collision_corrected_origin_time = np.average(
                    values,
                    weights=weights,
                )
                setattr(
                    node,
                    self._assigned_property,
                    collision_corrected_origin_time,
                )

        return trie
