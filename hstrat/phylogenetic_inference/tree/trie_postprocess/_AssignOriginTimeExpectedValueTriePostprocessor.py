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
    """Functor to assign origin time property to trie nodes using expected
    values over the distribution of possible differentia collisions.

    Computes the origin time of trie nodes based on the expected value, taking
    into account the probability of differentia collision and the prior
    distribution expected for ancestor origin times.
    """

    _assigned_property: str  # property name for assigned origin time
    _prior: object  # prior expectation for ancestor origin times

    def __init__(
        self: "AssignOriginTimeExpectedValueTriePostprocessor",
        prior: object,
        assigned_property: str = "origin_time",
    ) -> None:
        """Initialize functor instance.

        Parameters
        ----------
        prior : object
            The prior distribution used to calculate expected values.
        assigned_property : str, default "origin_time"
            The property name for the assigned origin time.
        """
        self._assigned_property = assigned_property
        self._prior = prior

    def __call__(
        self: "AssignOriginTimeExpectedValueTriePostprocessor",
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
