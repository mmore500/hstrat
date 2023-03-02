import collections
import random

import anytree
import numpy as np

from ...._auxiliary_lib import generate_n
from ._TrieInnerNode import TrieInnerNode


def unzip_trie_expected_collisions(
    trie: TrieInnerNode,
    p_differentia_collision: float,
) -> None:

    # exclude root node --- assume does share MRCA
    num_nodes = sum(
        1 for node in anytree.PreOrderIter(trie) if node.parent is not None
    )
    expected_collisions = int(p_differentia_collision * num_nodes)

    node_targets = collections.Counter(
        generate_n(lambda: random.randrange(0, num_nodes), expected_collisions)
    )

    for i, node in enumerate(anytree.PostOrderIter(trie)):
        for __ in range(node_targets[i]):
            if node.parent is not None:
                preexisting_parent = node.parent
                node.parent = node.parent.parent
                if preexisting_parent.is_leaf:
                    # detach
                    preexisting_parent.parent = None
