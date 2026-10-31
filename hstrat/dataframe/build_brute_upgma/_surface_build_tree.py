import logging
import typing

import polars as pl
import tqdm

from ..._auxiliary_lib import (
    log_context_duration,
    log_memory_usage,
    warn_experimental,
)
from ...phylogenetic_inference.tree.trie_postprocess import (
    NopTriePostprocessor,
)
from .._impl._assemble_tip_tree import assemble_tip_tree
from .._impl._origin_time_cpp_impl_stub import brute_upgma
from .._impl._surface_explode_tips import (
    coalesce_dstream_data_id,
    empty_surface_tips,
    surface_explode_tips,
    tips_cpp_args,
)


@warn_experimental
def surface_build_tree(
    df: pl.DataFrame,
    *,
    drop_dstream_metadata: typing.Optional[bool] = None,
    exploded_slice_size: int = 1_000_000,
    mp_context: str = "spawn",
    mp_pool_size: int = 1,
    trie_postprocessor: typing.Callable = NopTriePostprocessor(),
    # ^^^ NopTriePostprocessor is stateless, so is safe as default value
) -> pl.DataFrame:
    """End-to-end interface to tree reconstruction for surface-based
    genome annotations, by average-linkage UPGMA over all tree-free
    pairwise origin-time estimates.

    Pairwise estimates are unbiased with respect to spurious differentia
    collisions. Clustering repeatedly merges the pair of clusters with the
    latest mean pairwise estimate (i.e., the most recently diverged). Node
    times are mean pairwise estimates between their children's tips, so
    they sum to the total of pairwise estimates over all tip pairs.

    Evaluates all pairs, so time and memory grow quadratically with the
    number of genomes. Intended as a reference for smaller datasets; see
    `hstrat.dataframe.build_trie_upgma` for a scalable alternative.

    Parameters
    ----------
    df : pl.DataFrame
        The input DataFrame containing packed data with required columns, one
        row per genome.

        Schema as for `hstrat.dataframe.build_trie.surface_build_tree`.

    drop_dstream_metadata : bool or None, default None
        Drop all dstream/downstream columns from the output?

        If None (default), some metadata columns are dropped.
        If False, all dstream/downstream columns are retained.
        If True, raises NotImplementedError.

    exploded_slice_size : int, default 1_000_000
        Number of rows to process at once. Lower values reduce memory usage.

    mp_context : str, default 'spawn'
        Multiprocessing context to use for parallel processing.

    mp_pool_size : int, default 1
        Number of worker processes for unpacking genome data.

    trie_postprocessor : Callable, default `hstrat.NopTriePostprocessor()`
        Tree postprocess functor, applied to the polars phylogeny before it
        is returned.

        Must take `trie` of type `polars.DataFrame`,
        `p_differentia_collision` of type `float`, `mutate` of type `bool`,
        and `progress_wrap` of type `Callable` params. Must return
        postprocessed phylogeny.

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
        - 'origin_time' : pl.Float64
            - Estimated origin time for phylogeny nodes, in generations
              elapsed since founding ancestor.
            - Corresponds to `dstream_T` - 1 - `dstream_S` for leaf nodes.
        - 'dstream_data_id' : pl.UInt64
            - Identifier of genome, for leaf nodes; null for inner nodes.

        Additional user-defined columns will be forwarded from the input
        DataFrame onto leaf nodes.

        The tree is binary, with a single root. Note that the alife-standard
        `ancestor_list` column is not included in the output.
    """
    logging.info("surface_build_tree begin")

    df = coalesce_dstream_data_id(df.lazy().collect())

    if df.is_empty():
        tips = empty_surface_tips()
        parent, time = [], []
    else:
        logging.info("surface_build_tree running surface_explode_tips...")
        tips = surface_explode_tips(
            df,
            exploded_slice_size=exploded_slice_size,
            mp_context=mp_context,
            mp_pool_size=mp_pool_size,
        )

        logging.info("surface_build_tree running brute_upgma...")
        with log_context_duration("brute_upgma", logging.info):
            parent, time = brute_upgma(*tips_cpp_args(tips), tqdm.tqdm)
        log_memory_usage(logging.info)

    logging.info("surface_build_tree running assemble_tip_tree...")
    df = assemble_tip_tree(
        df,
        tips,
        parent,
        time,
        drop_dstream_metadata=drop_dstream_metadata,
        trie_postprocessor=trie_postprocessor,
    )

    logging.info("surface_build_tree complete")
    return df
