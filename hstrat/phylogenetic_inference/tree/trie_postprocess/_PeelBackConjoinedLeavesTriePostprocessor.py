import typing

from ...._auxiliary_lib import (
    AnyTreeFastLeafIter,
    anytree_iterative_deepcopy,
    anytree_peel_sibling_to_cousin,
)
from .._impl import TrieInnerNode


class PeelBackConjoinedLeavesTriePostprocessor:
    """Functor to separate any TrieLeafNode instances that are direct siblings.

    Corrects for guaranteed-spurious differentia collisions among most- recent
    strata.
    """

    def __call__(
        self: "PeelBackConjoinedLeavesTriePostprocessor",
        trie: TrieInnerNode,
        p_differentia_collision: float,
        mutate: bool = False,
        progress_wrap: typing.Callable = lambda x: x,
    ) -> TrieInnerNode:
        """Peel apart any `TrieLeafNode` nodes that are direct siblings.

        Without reproduction dynamics that allow columns to be cloned without
        stratum deposit, two hereditary stratigraphic columns can only share
        their most-recent strata by collision.

        Clones the sibling leaves' parent node and attaches it to the
        the siblings' grandparent node. One sibling node is then grafted away
        from its original parent and attached onto the newly cloned parent node
        as a child. The original parent node is left in place with any
        remaining children. This process is repeated until no `TrieLeafNode`'s
        remain as direct siblings.

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
        """
        if not mutate:
            trie = anytree_iterative_deepcopy(
                trie, progress_wrap=progress_wrap
            )

        for leaf in progress_wrap(AnyTreeFastLeafIter(trie)):
            if sum(1 for __ in leaf.parent.outer_children) > 1:
                anytree_peel_sibling_to_cousin(leaf)

        return trie
