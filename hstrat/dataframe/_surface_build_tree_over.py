import logging
import typing

from phyloframe import legacy as pfl
import polars as pl

from ._surface_build_tree import surface_build_tree


def surface_build_tree_over(
    df: typing.Union[pl.DataFrame, pl.LazyFrame],
    *,
    partition_by: typing.Union[
        str,
        pl.Expr,
        typing.Sequence[typing.Union[str, pl.Expr]],
    ],
    progress_wrap: typing.Callable = lambda x: x,
    **kwargs,
) -> pl.DataFrame:
    """Interface for end-to-end tree reconstruction over distinct
    subsets of surface-based genome annotations.

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
    progress_wrap : Callable, optional
        Pass tqdm or equivalent to display a progress bar.
    **kwargs
        Forwarded to `surface_build_tree`.

    Returns
    -------
    pl.DataFrame
        The concatenated estimated phylogenetic trees in alife standard
        format, with unique taxon ids.

        Refer to `surface_build_tree` for schema details.

    Notes
    -----
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

    df = df.lazy().with_columns(*partition_by).collect()
    schema = df.schema

    return pfl.alifestd_aggregate_phylogenies_polars(
        surface_build_tree(
            group, **kwargs
        ).with_columns(  # forward partition key onto all rows, incl. non-leaf
            pl.lit(value, dtype=schema[name]).alias(name)
            for name, value in zip(partition_names, key)
        )
        for key, group in progress_wrap(
            df.group_by(partition_names, maintain_order=True),
        )
    )
