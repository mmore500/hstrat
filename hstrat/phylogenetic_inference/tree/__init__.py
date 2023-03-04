"""Functions to reconstruct a phylogenetic tree from extant hereditary strata."""

from . import trie_postprocess
from ._build_tree import build_tree
from ._build_tree_nj import build_tree_nj
from ._build_tree_trie import build_tree_trie
from ._build_tree_upgma import build_tree_upgma

__all__ = [
    "build_tree_nj",
    "build_tree_trie",
    "build_tree_upgma",
    "build_tree",
    "trie_postprocess",
]

from ..._auxiliary_lib import launder_impl_modules as _launder

_launder([eval(item) for item in __all__], __name__)
del _launder  # prevent name from leaking
