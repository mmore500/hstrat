import typing

from ...._auxiliary_lib import (
    AnyTreeFastPreOrderIter,
    anytree_iterative_deepcopy,
)
from ...priors import ArbitraryPrior
from .._impl import TrieInnerNode, TrieLeafNode


class AssignOriginTimeNaiveTriePostprocessor:
    """Functor to assign origin time property to trie nodescalculated as the
    average of the node's rank and the minimum rank among its children.

    Optionally calculates origin time expected value over this interval for
    a provided prior distribution.
    """

    _assigned_property: str  # property name for assigned origin time
    _prior: object  # prior expectation for ancestor origin times

    def __init__(
        self: "AssignOriginTimeNaiveTriePostprocessor",
        prior: object = ArbitraryPrior(),  # ok as kwarg; immutable
        assigned_property: str = "origin_time",
    ) -> None:
        """Initialize functor instance.

        Parameters
        ----------
        prior : object, default ArbitraryPrior()
            Prior distribution of ancestor origin times.

            Used to calculate interval means.
        assigned_property : str, default "origin_time"
            The property name for the assigned origin time.
        """
        self._assigned_property = assigned_property
        self._prior = prior

    def __call__(
        self: "AssignOriginTimeNaiveTriePostprocessor",
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

            Not used in the current implementation.
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

        for node in progress_wrap(AnyTreeFastPreOrderIter(trie)):
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
                    ),  # endpoint is exclusive
                )
                setattr(
                    node,
                    self._assigned_property,
                    min(
                        interval_mean,
                        min(
                            (child.rank for child in node.children),
                            default=interval_mean,
                        ),
                    ),
                )

            assert hasattr(node, self._assigned_property)

        return trie
