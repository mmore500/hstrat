import logging
import typing

from phyloframe import legacy as pfl
import polars as pl
from tqdm import tqdm

from ..phylogenetic_inference.tree.trie_postprocess import NopTriePostprocessor
from ._surface_build_tree import surface_build_tree


def surface_build_tree_over(
    df: typing.Union[pl.DataFrame, pl.LazyFrame],
    *,
    partition_by: typing.Union[
        str,
        pl.Expr,
        typing.Sequence[typing.Union[str, pl.Expr]],
    ],
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
    trie_postprocessor: typing.Callable = NopTriePostprocessor(),
    # ^^^ NopTriePostprocessor is stateless, so is safe as default value
    progress_wrap: typing.Callable = tqdm,
) -> pl.DataFrame:
    """Partitioned interface to end-to-end tree reconstruction for
    surface-based genome annotations.

    Splits input rows into partitions by distinct values of `partition_by`
    column(s) or expression(s), and applies `surface_build_tree`
    independently to each partition. Reconstructed phylogenies are then
    concatenated as independent trees, with taxon ids reassigned to prevent
    collisions. Genomes in different partitions are never placed in a shared
    tree.

    Parameters
    ----------
    df : pl.DataFrame or pl.LazyFrame
        The input DataFrame containing packed data with required columns, one
        row per genome.

        Refer to `surface_build_tree` for schema details.
    partition_by : str, pl.Expr, or sequence of str and pl.Expr
        Column name(s) or expression(s) to partition rows by.

        Expressions are added to input data as with `with_columns`, so name
        derived keys via `.alias`. Partition key values are forwarded to all
        output rows, including inner tree nodes.
    progress_wrap : Callable, default `tqdm`
        Wrapper applied to the partition iterator, e.g., to display a
        progress bar.

    Other parameters are as for `surface_build_tree`.

    Returns
    -------
    pl.DataFrame
        The concatenated estimated phylogenetic trees in alife standard
        format, with unique taxon ids.

        Refer to `surface_build_tree` for schema details.

    Notes
    -----
    If not provided, 'dstream_data_id' is assigned from row number before
    partitioning, so values are unique across partitions.

    Partitions are ordered by first appearance in input data.

    See Also
    --------
    surface_build_tree :
        Reconstruct a single tree from all genomes.
    phyloframe.legacy.alifestd_aggregate_phylogenies_polars :
        Concatenate independent phylogenies, reassigning ids.
    """
    if isinstance(partition_by, (str, pl.Expr)):
        partition_by = [partition_by]
    partition_by = [
        pl.col(k) if isinstance(k, str) else k for k in partition_by
    ]
    partition_names = [expr.meta.output_name() for expr in partition_by]
    logging.info(f"surface_build_tree_over partitioning by {partition_names}")

    df = (
        df.lazy()
        .with_columns(  # ensure unique across partitions
            dstream_data_id=pl.coalesce(
                pl.col("^dstream_data_id$"),
                pl.int_range(pl.len(), dtype=pl.UInt64),
            ).cast(pl.UInt64),
        )
        .with_columns(*partition_by)
        .collect()
    )
    schema = df.schema

    return pfl.alifestd_aggregate_phylogenies_polars(
        surface_build_tree(
            group,
            collapse_unif_freq=collapse_unif_freq,
            check_trie_invariant_freq=check_trie_invariant_freq,
            check_trie_invariant_after_collapse_unif=check_trie_invariant_after_collapse_unif,
            drop_dstream_metadata=drop_dstream_metadata,
            exploded_slice_size=exploded_slice_size,
            mp_context=mp_context,
            mp_pool_size=mp_pool_size,
            pa_source_type=pa_source_type,
            shuffle_over_same_T_seed=shuffle_over_same_T_seed,
            delete_trunk=delete_trunk,
            trie_postprocessor=trie_postprocessor,
        ).with_columns(  # forward partition key onto all rows, incl. inner
            pl.lit(value, dtype=schema[name]).alias(name)
            for name, value in zip(partition_names, key)
        )
        for key, group in progress_wrap(
            df.group_by(partition_names, maintain_order=True),
        )
    )
