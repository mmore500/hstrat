import anytree
import numpy as np

from ._TrieInnerNode import TrieInnerNode
from ._TrieLeafNode import TrieLeafNode


def assign_trie_origin_times_naive(trie: TrieInnerNode) -> None:
    for node in anytree.PreOrderIter(trie):
        if node.is_leaf:
            node.origin_time = node.rank + 0.5
            assert isinstance(node, TrieLeafNode)
        elif node.parent is None:
            node.origin_time = 0
        else:
            node.origin_time = np.mean(
                (node.rank, min(child.rank for child in node.children) - 1)
            )
