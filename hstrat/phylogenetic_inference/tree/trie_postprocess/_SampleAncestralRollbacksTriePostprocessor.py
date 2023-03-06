import contextlib
import copy
import random
import typing

import anytree
import opytional as opyt

from ...._auxiliary_lib import (
    RngStateContext,
    anytree_calc_leaf_counts,
    anytree_has_grandparent,
    anytree_has_sibling,
    anytree_peel_sibling_to_cousin,
)
from .._impl import TrieInnerNode


def _sample_ancestral_rollbacks(
    trie: TrieInnerNode,
    p_differentia_collision: float,
    mutate: bool = False,
) -> TrieInnerNode:
    """Implementation detail for `SampleAncestralRollbacks.__call__`.

    See `SampleAncestralRollbacks.__call__` for parameter descriptions.
    """
    if not mutate:
        trie = copy.deepcopy(trie)

    eligible_nodes = {
        id(node): node
        for node in anytree.PreOrderIter(trie)
        if anytree_has_sibling(node) and anytree_has_grandparent(node)
    }
    # sequence data structure allows efficient random choice
    possibly_eligible_node_ids = [*eligible_nodes.keys()]

    # 2x number of leaves is the number of nodes in a strictly bifurcating tree
    unzip_opportunities = 2 * len(trie.leaves)
    expected_collisions = int(
        p_differentia_collision * unzip_opportunities
    )

    leaf_counts = anytree_calc_leaf_counts(trie)
    del leaf_counts[id(trie)]  # exclude root
    max_unzips = sum(leaf_counts.values()) - len(
        leaf_counts
    )  # -1 per; last sibling always ineligible for unzip
    assert max_unzips >= unzip_opportunities >= expected_collisions

    remaining_collisions = expected_collisions
    while remaining_collisions:
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


class SampleAncestralRollbacksTriePostprocessor:

    _seed: typing.Optional[int]

    def __init__(
        self: "SampleAncestralRollbacksTriePostprocessor",
        seed: typing.Optional[int] = None,
    ) -> None:
        self._seed = seed

    def __call__(
        self: "SampleAncestralRollbacksTriePostprocessor",
        trie: TrieInnerNode,
        p_differentia_collision: float,
        mutate: bool = False,
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
        seed: int, default
            Controls sampling decisions in the algorithm.

            Pass an int for reproducible output across multiple function calls.
            The default value, 1, ensures reproducible output. Pass None to use
            existing RNG context directly.

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
            return _sample_ancestral_rollbacks(
                trie=trie,
                p_differentia_collision=p_differentia_collision,
                mutate=mutate,
            )
