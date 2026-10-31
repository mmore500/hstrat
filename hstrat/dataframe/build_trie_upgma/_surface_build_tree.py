import logging
import typing

from phyloframe import legacy as pfl
import polars as pl

from ..._auxiliary_lib import warn_experimental
from ...phylogenetic_inference.tree.trie_postprocess import (
    NopTriePostprocessor,
)
from .._impl import surface_unpack_reconstruct
from .._impl._assemble_tip_tree import assemble_tip_tree
from .._impl._origin_time_cpp_impl_stub import scaffold_upgma
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
    collapse_unif_freq: int = 1,
    drop_dstream_metadata: typing.Optional[bool] = None,
    exploded_slice_size: int = 1_000_000,
    mp_context: str = "spawn",
    mp_pool_size: int = 1,
    pa_source_type: str = "memory_map",
    num_candidates: int = 5,
    candidate_pool_size: int = 10,
    num_samples: int = 64,
    direct_max: int = 64,
    sampling_seed: int = 1,
    trie_postprocessor: typing.Callable = NopTriePostprocessor(),
    # ^^^ NopTriePostprocessor is stateless, so is safe as default value
) -> pl.DataFrame:
    """End-to-end interface to tree reconstruction for surface-based
    genome annotations, by average-linkage UPGMA over tree-free pairwise
    origin-time estimates, scaffolded by a reconstructed trie.

    Pairwise estimates are unbiased with respect to spurious differentia
    collisions. Clustering merges the pair of clusters with the latest
    mean pairwise estimate (i.e., the most recently diverged), using
    candidate neighbors from a trie walk, so all pairs need not be
    evaluated. Linkage values are exact for small cluster pairs and sampled
    otherwise; merges decided on sampled values get exact heights, and
    inverted parent/child heights are pooled. Node times therefore sum to
    the total of pairwise estimates over all tip pairs.

    Identical genomes are clustered together first.

    Parameters
    ----------
    df : pl.DataFrame
        The input DataFrame containing packed data with required columns, one
        row per genome.

        Schema as for `hstrat.dataframe.build_trie.surface_build_tree`.

    collapse_unif_freq : int, default 1
        How often should dropped unifurcations be garbage collected, while
        building the scaffold trie?

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
        Number of worker processes for exploding slices in parallel.

    pa_source_type : str, default 'memory_map'
        PyArrow type to use for exploded chunks (i.e., "memory_map" or
        "OSFile").

    num_candidates : int, default 5
        Number of closest candidate neighbors kept per genome.

    candidate_pool_size : int, default 10
        Number of trie-adjacent genomes evaluated per genome to choose
        candidate neighbors.

    num_samples : int, default 64
        Number of sampled tip pairs used to estimate linkage between large
        clusters.

    direct_max : int, default 64
        Linkage between clusters is computed exactly when the product of
        their sizes is at most this.

    sampling_seed : int, default 1
        Random seed for sampled linkage values.

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

        logging.info(
            "surface_build_tree running surface_unpack_reconstruct...",
        )
        trie = surface_unpack_reconstruct(
            df.select("data_hex", "^dstream_.*$", "^downstream_.*$"),
            collapse_unif_freq=collapse_unif_freq,
            exploded_slice_size=exploded_slice_size,
            mp_context=mp_context,
            mp_pool_size=mp_pool_size,
            pa_source_type=pa_source_type,
        )

        if not pfl.alifestd_has_contiguous_ids_polars(trie):
            raise NotImplementedError("non-contiguous trie ids not supported")

        logging.info("surface_build_tree running scaffold_upgma...")
        parent, time, stats = scaffold_upgma(
            *tips_cpp_args(tips),
            trie["ancestor_id"].cast(pl.Int64).to_numpy(),
            tips.tip_of_node(trie["dstream_data_id"]),
            k=num_candidates,
            pool_size=candidate_pool_size,
            n_samples=num_samples,
            direct_max=direct_max,
            seed=sampling_seed,
        )
        del trie
        logging.info(f"scaffold_upgma stats: {stats}")

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
