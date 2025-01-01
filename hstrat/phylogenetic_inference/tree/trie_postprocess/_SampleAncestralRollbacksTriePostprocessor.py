import contextlib
import itertools as it
import random
import typing

import opytional as opyt
import pandas as pd
import polars as pl

from ...._auxiliary_lib import (
    AnyTreeFastPreOrderIter,
    RngStateContext,
    anytree_calc_leaf_counts,
    anytree_has_grandparent,
    anytree_has_sibling,
    anytree_iterative_deepcopy,
    anytree_peel_sibling_to_cousin,
)
from .._impl import TrieInnerNode
from ._detail import TriePostprocessorBase


def _call_anytree(
    trie: TrieInnerNode,
    p_differentia_collision: float,
    progress_wrap: typing.Callable,
) -> TrieInnerNode:
    """Implementation detail for `SampleAncestralRollbacks.__call__`.

    See `SampleAncestralRollbacks.__call__` for parameter descriptions.
    """
    eligible_nodes = {
        id(node): node
        for node in AnyTreeFastPreOrderIter(trie)
        if anytree_has_sibling(node) and anytree_has_grandparent(node)
    }
    # sequence data structure allows efficient random choice
    possibly_eligible_node_ids = [*eligible_nodes.keys()]

    # number of internal nodes approx equal to the number of branching nodes in
    # a strictly bifurcating/unifurcating tree
    # ... correction for multifurcations (i.e., due to strong selection
    # pressure) should be considered in the future (including whether such
    # corections are necessary in the first place)
    num_leaves = sum(node.is_leaf for node in AnyTreeFastPreOrderIter(trie))
    unzip_opportunities = num_leaves

    if p_differentia_collision <= 0.5:
        # 1 + 1/x + 1/x^2 + ... = x / (x - 1)
        # expected number of successive collisions:
        # 1/x + 1/x^2 + 1/x^3 + ... =  1 / (x - 1)
        # p = 1/x -> x = 1/p
        #  1/x + 1/x^2 + ... = 1 / (1/p - 1)
        # 1/x + 1/x^2 + ... = p / (1 - p)
        # note: does not account for limitations in the number of possible
        # collisions due to tree depth
        collision_succession_corrected_expectation_per_opportunity = (
            p_differentia_collision / (1 - p_differentia_collision)
        )
    else:
        # allow feeding unrealistic p for bounds testing
        collision_succession_corrected_expectation_per_opportunity = (
            p_differentia_collision
        )

    # note:
    # this estimates the expected value of the number of collisions;
    # so some possible outcomes like all max_unzips being performed or no
    # unzips being performed will never occur;
    # an alternate approach would be to sample the number of collisions...
    # the number of collisions might be drawn from a binomial distribution
    # but some care would have to be taken to consider the possibility of
    # successive collisions where the MRCA is rolled back more than one
    # position
    expected_collisions = int(
        collision_succession_corrected_expectation_per_opportunity
        * unzip_opportunities
    )

    def calc_max_unzips() -> bool:
        leaf_counts = anytree_calc_leaf_counts(trie)
        del leaf_counts[id(trie)]  # exclude root
        max_unzips = sum(leaf_counts.values()) - len(
            leaf_counts
        )  # -1 per; last sibling always ineligible for unzip
        return max_unzips

    expected_collisions = min(expected_collisions, calc_max_unzips())

    remaining_collisions = expected_collisions

    progress = iter(progress_wrap(it.count()))
    while remaining_collisions:
        next(progress)
        assert possibly_eligible_node_ids
        target_idx = random.randrange(len(possibly_eligible_node_ids))
        target_id = possibly_eligible_node_ids[target_idx]
        if target_id not in eligible_nodes:
            # swap and pop to update possibly_eligible_node_ids
            # to match eligible_nodes
            (
                possibly_eligible_node_ids[-1],
                possibly_eligible_node_ids[target_idx],
            ) = (
                possibly_eligible_node_ids[target_idx],
                possibly_eligible_node_ids[-1],
            )
            assert possibly_eligible_node_ids[-1] == target_id
            possibly_eligible_node_ids.pop()
            continue

        target_node = eligible_nodes[target_id]

        original_parent = target_node.parent
        grandparent = target_node.parent.parent
        target_node = eligible_nodes[target_id]
        anytree_peel_sibling_to_cousin(target_node)
        remaining_collisions -= 1

        # target node is now ineligible
        # swap and pop out of possibly_eligible_node_ids, eligible_nodes
        (
            possibly_eligible_node_ids[-1],
            possibly_eligible_node_ids[target_idx],
        ) = (
            possibly_eligible_node_ids[target_idx],
            possibly_eligible_node_ids[-1],
        )
        assert possibly_eligible_node_ids[-1] == target_id
        possibly_eligible_node_ids.pop()
        eligible_nodes.pop(target_id)

        # is target's (possibly lone) sibling now ineligible?
        if len(original_parent.children) == 1:
            eligible_nodes.pop(id(original_parent.children[0]))

        for sibling in grandparent.children:
            # peeled off parent is always newly eligible
            # peeled from parent might be newly eligible
            if len(grandparent.children) == 2 or sibling is target_node.parent:
                if anytree_has_grandparent(sibling):
                    assert id(sibling) not in eligible_nodes
                    possibly_eligible_node_ids.append(id(sibling))
                    eligible_nodes[id(sibling)] = sibling
                    assert anytree_has_sibling(sibling)
                    assert anytree_has_grandparent(sibling)

    return trie


class SampleAncestralRollbacksTriePostprocessor(
    TriePostprocessorBase,
):
    """Functor to correct for systematic overestimation of relatedness by
    sampling a compensatory adjustment to trie topology."""

    _seed: typing.Optional[int]

    def __init__(
        self: "SampleAncestralRollbacksTriePostprocessor",
        seed: typing.Optional[int] = None,
    ) -> None:
        """Initialize functor instance.

        Parameters:
        ----------
        seed: int, default
            Controls sampling decisions in the algorithm.

            Pass an int for reproducible output across multiple function calls.
            The default value, 1, ensures reproducible output. Pass None to use
            existing RNG context directly.
        """

        self._seed = seed

    def __call__(
        self: "SampleAncestralRollbacksTriePostprocessor",
        trie: TrieInnerNode,
        p_differentia_collision: float,
        mutate: bool = False,
        progress_wrap: typing.Callable = lambda x: x,
    ) -> TrieInnerNode:
        """Compensate for bias towards overestimating relatedness due to
        spurious differentia collisions.

        Each rollback operation alters the tree as if a single spurious
        collision had occured; a single branch is adjusted to exhibit the next-
        most-ancient last commonality.

        The number of rollback operations is calculated from the number of
        possible spurious collisions and the probability of spurious collision.
        Unzip targets are sampled randomly using the standard library `random`
        module.

        Parameters:
        ----------
        trie : TrieInnerNode
            The root node of the trie to be unzipped.
        p_differentia_collision : float
            The multiplicative inverse of the number of possible
            differentia.

            This fraction of possible rollbacks are performed.
        mutate : bool, default False
            Are side effects on the input argument `trie` allowed?
        progress_wrap : typing.Callable, optional
            Pass tqdm or equivalent to report progress.

        Returns
        -------
        TrieInnerNode
            The postprocessed trie.

        Notes:
        ------
        This function assumes underlying shared genesis, so the root node of the
        trie is not eligible for rollback.
        """
        with opyt.apply_if_or_value(
            self._seed,
            RngStateContext,
            contextlib.nullcontext(),
        ):
            if isinstance(trie, TrieInnerNode):
                if not mutate:
                    trie = anytree_iterative_deepcopy(
                        trie, progress_wrap=progress_wrap
                    )
                return _call_anytree(
                    trie,
                    p_differentia_collision,
                    progress_wrap=progress_wrap,
                )
            elif isinstance(trie, (pl.DataFrame, pd.DataFrame)):
                raise NotImplementedError
            else:
                raise TypeError
