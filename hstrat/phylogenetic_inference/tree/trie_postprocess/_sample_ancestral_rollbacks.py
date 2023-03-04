import contextlib
import copy
import random
import typing

import anytree

from ...._auxiliary_lib import (
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
    """Implementation detail for `sample_ancestral_rollbacks`.

    See `sample_ancestral_rollbacks` for parameter descriptions.
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

    leaf_counts = anytree_calc_leaf_counts(trie)
    del leaf_counts[id(trie)]  # exclude root
    num_possible_unzips = sum(leaf_counts.values()) - len(
        leaf_counts
    )  # -1 per; last sibling always ineligible for unzip
    expected_collisions = int(p_differentia_collision * num_possible_unzips)

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


def sample_ancestral_rollbacks(
    trie: TrieInnerNode,
    p_differentia_collision: float,
    mutate: bool = False,
    seed: typing.Optional[int] = None,
) -> TrieInnerNode:
    """Compensate for bias towards overestimating relatedness due to spurious
    differentia collisions.

    Each rollback operation alters the tree as if a single spurious collision
    had occured; a single branch is adjusted to exhibit the next-most-ancient last commonality.

    The number of rollback operations is calculated from the number of possible
    spurious collisions and the probability of spurious collision. Unzip
    targets are sampled randomly using the standard library `random` module.

    The trie is modified inplace.

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

        Pass an int for reproducible output across multiple function calls. The
        default value, 1, ensures reproducible output. Pass None to use
        existing RNG context directly.

    Notes:
    ------
    This function assumes underlying shared genesis, so the root node of the
    trie is not eligible for rollback.
    """
    with opyt.apply_if_or_value(
        seed,
        RngStateContext,
        contextlib.nullcontext,
    ):
        return _build_tree_trie_ensemble(
            population=population,
            postprocessors=postprocessors,
            taxon_labels=taxon_labels,
            force_common_ancestry=force_common_ancestry,
            progress_wrap=progress_wrap,
        )
