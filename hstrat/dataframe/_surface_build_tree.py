import logging
import typing

import polars as pl

from ..phylogenetic_inference.tree.trie_postprocess import NopTriePostprocessor
from ._surface_postprocess_trie import surface_postprocess_trie
from ._surface_unpack_reconstruct import surface_unpack_reconstruct


def surface_build_tree(
    df: pl.DataFrame,
    *,
    exploded_slice_size: int = 1_000_000,
    trie_postprocessor: typing.Callable = NopTriePostprocessor(),
    # ^^^ NopTriePostprocessor is stateless, so is safe as default value
) -> pl.DataFrame:
    logging.info("surface_build_tree begin")

    logging.info("surface_build_tree running surface_unpack_reconstruct...")
    df = surface_unpack_reconstruct(
        df, exploded_slice_size=exploded_slice_size
    )

    logging.info("surface_build_tree running surface_postprocess_trie...")
    df = surface_postprocess_trie(df, trie_postprocessor=trie_postprocessor)

    logging.info("surface_build_tree complete")
    return df
