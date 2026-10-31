import logging
import typing

import polars as pl

from ...phylogenetic_inference.tree.trie_postprocess import (
    CompoundTriePostprocessor,
    NopTriePostprocessor,
)
from .._impl import surface_postprocess_trie, surface_unpack_reconstruct
from .._impl._cross_pair_origin_time import (
    CROSS_PAIR_COUNT,
    CROSS_PAIR_SUM,
    AssignOriginTimeCrossPairTriePostprocessor,
    attach_cross_pair_sums,
)
from .._impl._surface_explode_tips import (
    coalesce_dstream_data_id,
    surface_explode_tips,
)


def surface_build_tree(
    df: pl.DataFrame,
    *,
    collapse_unif_freq: int = 1,
    check_trie_invariant_freq: int = 0,
    check_trie_invariant_after_collapse_unif: bool = False,
    drop_dstream_metadata: typing.Optional[bool] = None,
    exploded_slice_size: int = 1_000_000,
    mp_context: str = "spawn",
    mp_pool_size: int = 1,
    pa_source_type: str = "memory_map",
    shuffle_over_same_T_seed: typing.Optional[int] = None,
    delete_trunk: bool = True,
    pool_inversions: bool = True,
    trie_postprocessor: typing.Callable = NopTriePostprocessor(),
    # ^^^ NopTriePostprocessor is stateless, so is safe as default value
) -> pl.DataFrame:
    """End-to-end interface to tree reconstruction for surface-based
    genome annotations, with cross-pair origin-time estimates.

    Reconstructs a trie as `hstrat.dataframe.build_trie.surface_build_tree`
    does. Before the trie is postprocessed, each node is assigned the mean
    of tree-free pairwise origin-time estimates over all tip pairs that
    first split at that node. Pairwise estimates are unbiased with respect
    to spurious differentia collisions, and cross-pair means sum to the
    total of estimates over all tip pairs, for any reconstructed topology.

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

    drop_dstream_metadata : bool or None, default None
        Drop all dstream/downstream columns from the output?

        If None (default), some metadata columns are dropped.
        If False, all dstream/downstream columns are retained.
        If True, raises NotImplementedError.

    collapse_unif_freq : int, default 1
        How often should dropped unifurcations be garbage collected?

    exploded_slice_size : int, default 1_000_000
        Number of rows to process at once. Lower values reduce memory usage.

    mp_context : str, default 'spawn'
        Multiprocessing context to use for parallel processing.

    mp_pool_size : int, default 1
        Number of worker processes for exploding slices in parallel.

        When 1, a single producer process is used (original behavior).
        When greater than 1, a multiprocessing pool is used with ordered
        results via ``Pool.imap``.

    pa_source_type : str, default 'memory_map'
        PyArrow type to use for exploded chunks (i.e., "memory_map" or
        "OSFile").

    shuffle_over_same_T_seed : int or None, default None
        If not None, shuffle rows within same-dstream_T groups after
        sorting but before exploding. The value is used as the random
        seed for reproducibility. Set to None to disable (default).

    delete_trunk : bool, default `True`
        Should trunk nodes with rank less than `dstream_S` be deleted?

        Trunk deletion accounts for "dummy" strata added to fill hstrat surface
        for founding ancestor(s), by segregating subtrees with distinct
        founding strata into independent trees.

    trie_postprocessor : Callable, default `hstrat.NopTriePostprocessor()`
        Tree postprocess functor.

        Must take `trie` of type `pandas.DataFrame`,
        `p_differentia_collision` of type `float`, `mutate` of type `bool`, and
        `progress_wrap` of type `Callable` params. Must return postprocessed
        trie (type `pd.DataFrame`).

        Applied after cross-pair origin times are assigned. To apply
        multiple postprocessors, use `hstrat.CompoundTriePostprocessor`.

    pool_inversions : bool, default `True`
        Pool inverted parent/child origin-time estimates to their
        pair-count-weighted mean, so that ancestors are never assigned later
        times than descendants? Pooling preserves the total of estimates
        over all tip pairs.

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
        - 'hstrat_rank' : pl.Int64
            - Num generations elapsed for ancestral differentia.
            - Corresponds to `dstream_Tbar` - `dstream_S` for inner nodes.
            - Corresponds to `dstream_T` - 1 - `dstream_S` for leaf nodes.

        Optional schema:
        - 'origin_time' : pl.Int64
            - Estimated origin time for phylogeny nodes, in generations elapsed
              since founding ancestor.

              Cross-pair mean of pairwise estimates for inner nodes, and
              `dstream_T` - 1 - `dstream_S` for leaf nodes, unless
              reassigned by the trie postprocessor.

        Additional user-defined columns will be forwarded from the input
        DataFrame. Any columns created by the trie postprocessor will also be
        included.

        Note that the alife-standard `ancestor_list` column is not included in
        the output.
    """
    logging.info("surface_build_tree begin")

    df = coalesce_dstream_data_id(df.lazy().collect())

    is_empty = df.is_empty()
    if not is_empty:
        logging.info("surface_build_tree running surface_explode_tips...")
        tips = surface_explode_tips(
            df,
            exploded_slice_size=exploded_slice_size,
            mp_context=mp_context,
            mp_pool_size=mp_pool_size,
        )

    logging.info("surface_build_tree running surface_unpack_reconstruct...")
    df = surface_unpack_reconstruct(
        df,
        collapse_unif_freq=collapse_unif_freq,
        check_trie_invariant_freq=check_trie_invariant_freq,
        check_trie_invariant_after_collapse_unif=check_trie_invariant_after_collapse_unif,
        drop_dstream_metadata=drop_dstream_metadata,
        exploded_slice_size=exploded_slice_size,
        mp_context=mp_context,
        mp_pool_size=mp_pool_size,
        pa_source_type=pa_source_type,
        shuffle_over_same_T_seed=shuffle_over_same_T_seed,
    )

    if not is_empty:
        logging.info("surface_build_tree running attach_cross_pair_sums...")
        df = attach_cross_pair_sums(df, tips)

    logging.info("surface_build_tree running surface_postprocess_trie...")
    df = surface_postprocess_trie(
        df,
        delete_trunk=delete_trunk,
        drop_dstream_metadata=drop_dstream_metadata,
        trie_postprocessor=CompoundTriePostprocessor(
            [
                AssignOriginTimeCrossPairTriePostprocessor(
                    pool_inversions=pool_inversions,
                ),
                trie_postprocessor,
            ],
        ),
    ).drop(CROSS_PAIR_SUM, CROSS_PAIR_COUNT, strict=False)

    logging.info("surface_build_tree complete")
    return df
