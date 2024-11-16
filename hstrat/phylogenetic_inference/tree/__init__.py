"""Functions to reconstruct a phylogenetic tree from extant hereditary strata."""

from . import trie_postprocess
from ..._auxiliary_lib import lazy_attach

__getattr__, __dir__, __all__ = lazy_attach(
    __name__,
    submodules=["trie_postprocess"],
    submod_attrs={
        "trie_postprocess": trie_postprocess.__all__,
        "_build_tree": ["build_tree"],
        "_build_tree_nj": ["build_tree_nj"],
        "_build_tree_searchtable": ["build_tree_searchtable"],
        "_build_tree_trie": ["build_tree_trie"],
        "_build_tree_trie_ensemble": ["build_tree_trie_ensemble"],
        "_build_tree_upgma": ["build_tree_upgma"],
    },
    should_launder=[
        "build_tree_nj",
        "build_tree_searchtable",
        "build_tree_trie",
        "build_tree_trie_ensemble",
        "build_tree_upgma",
        "build_tree",
        "trie_postprocess",
    ].__contains__,
)
del lazy_attach
