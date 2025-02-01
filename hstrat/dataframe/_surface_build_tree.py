import logging
import typing

import polars as pl

from ..phylogenetic_inference.tree.trie_postprocess import NopTriePostprocessor
from ._surface_postprocess_trie import surface_postprocess_trie
from ._surface_unpack_reconstruct import surface_unpack_reconstruct


def surface_build_tree(
    df: pl.DataFrame,
    *,
    collapse_unif_freq: int = 1,
    exploded_slice_size: int = 1_000_000,
    mp_context: str = "spawn",
    delete_trunk: bool = True,
    trie_postprocessor: typing.Callable = NopTriePostprocessor(),
    # ^^^ NopTriePostprocessor is stateless, so is safe as default value
) -> pl.DataFrame:
    """End-to-end interface to tree reconstruction for surface-based
    genome annotations. Reads raw hex genome data from tabular data
    file(s) and writes postprocessed phylogeny data to output file in
    alife standard format.

    Bundles `surface_unpack_reconstruct` and `surface_postprocess_trie`.
    Refer to corresponding docstrings/help messages for technical
    details on phylogeny reconstruction and postprocessing steps.

    Parameters
    ----------
    df : pl.DataFrame
        The input DataFrame containing packed data with required columns, one
        row per genome.

        Required schema:
            - 'data_hex' : pl.String
                - Raw genome data, with serialized dstream buffer and counter.
                - Represented as a hexadecimal string.
            - 'dstream_algo' : pl.Categorical
                - Name of downstream curation algorithm used.
                - e.g., 'dstream.steady_algo'
            - 'dstream_storage_bitoffset' : pl.UInt64
                - Position of dstream buffer field in 'data_hex'.
            - 'dstream_storage_bitwidth' : pl.UInt64
                - Size of dstream buffer field in 'data_hex'.
            - 'dstream_T_bitoffset' : pl.UInt64
                - Position of dstream counter field in 'data_hex'.
            - 'dstream_T_bitwidth' : pl.UInt64
                - Size of dstream counter field in 'data_hex'.
            - 'dstream_S' : pl.Uint32
                - Capacity of dstream buffer, in number of data items.

        Optional schema:
            - 'downstream_version' : pl.Categorical
                - Version of downstream library used to curate data items.
            - 'dstream_data_id' : pl.UInt64
                - Unique identifier for each data item.
                - If not provided, row number will be used as identifier.
            - 'downstream_exclude_exploded' : pl.Boolean
                - Should row be dropped after exploding unpacked data?
            - 'downstream_exclude_unpacked' : pl.Boolean
                - Should row be dropped after unpacking packed data?
            - 'downstream_validate_exploded' : pl.String, polars expression
                - Polars expression to validate exploded data.
            - 'downstream_validate_unpacked' : pl.String, polars expression
                - Polars expression to validate unpacked data.

    collapse_unif_freq : int, default 1
        How often should dropped unifurcations be garbage collected?

    exploded_slice_size : int, default 1_000_000
        Number of rows to process at once. Lower values reduce memory usage.

    mp_context : str, default 'spawn'
        Multiprocessing context to use for parallel processing.

    delete_trunk : bool, default `True`
        Should trunk nodes with rank less than `dstream_S` be deleted?

        Trunk deletion accounts for "dummy" strata added to fill hstrat surface
        for founding ancestor(s), by segregating subtrees with distinct
        founding strata into independent trees.

    trie_postprocessor : Callable, default `hstrat.NopTriePostprocessor()`
        Tree postprocess functor.

        Must take `trie` of type `pandas.DataFrame`,
        `p_differentia_collision` of type `float`, `mutate` of type `bool`, and
        `progress_wrap` of type `Callable` params. Must returned postprocessed
        trie (type `pd.DataFrame`).

        To apply multiple postprocessors, use
        `hstrat.CompoundTriePostprocessor`.

    Returns
    -------
    pl.DataFrame
        The output DataFrame containing the estimated phylogenetic tree in
        alife standard format, with the following columns:

        Required schema:
        - 'id' : pl.UInt64
            - Unique identifier for each taxon (RE alife standard format).
        - 'ancestor_id' : pl.UInt64
            - Unique identifier for ancestor taxon  (RE alife standard format).
        - 'hstrat_rank_from_t0' : pl.UInt64
            - Num generations elapsed for ancestral differentia.
            - Corresponds to `dstream_Tbar` - `dstream_S` for inner nodes.
            - Corresponds `dstream_T` - 1 - `dstream_S` for leaf nodes

        Optional schema:
        - 'origin_tme' : pl.UInt64
            - Estimated origin time for phylogeny nodes, in generations elapsed
              since fouding ancestor.

              Value depends on the trie postprocessor used.

        Additional user-defined columns will be forwarded from the input
        DataFrame. Any columns created by the trie postprocessor will also be
        included.

        Note that the alife-standard `ancestor_list` column is not included in
        the output."""
    logging.info("surface_build_tree begin")

    logging.info("surface_build_tree running surface_unpack_reconstruct...")
    df = surface_unpack_reconstruct(
        df,
        collapse_unif_freq=collapse_unif_freq,
        exploded_slice_size=exploded_slice_size,
        mp_context=mp_context,
    )

    logging.info("surface_build_tree running surface_postprocess_trie...")
    df = surface_postprocess_trie(
        df,
        delete_trunk=delete_trunk,
        trie_postprocessor=trie_postprocessor,
    )

    logging.info("surface_build_tree complete")
    return df
