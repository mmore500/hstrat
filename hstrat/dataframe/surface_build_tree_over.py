import logging
import os
import typing

import joinem
from joinem._dataframe_cli import _run_dataframe_cli
from phyloframe import legacy as pfl
import polars as pl
from tqdm import tqdm

from .._auxiliary_lib import (
    begin_prod_logging,
    get_hstrat_version,
    log_context_duration,
)
from .surface_build_tree import _create_parser as _create_base_parser
from .surface_build_tree import _make_build_tree_op

raw_message = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Partitioned interface to end-to-end tree reconstruction for surface-based genome annotations.
Splits input rows into partitions by `--partition-by` column(s) or expression(s), and applies `hstrat.dataframe.surface_build_tree` independently to each partition.
Reconstructed phylogenies are then concatenated as independent trees, with taxon ids reassigned to prevent collisions.

Genomes in different partitions are never placed in a shared tree.
All other flags, and input and output schemas, are as for `surface_build_tree`.
See `python3 -m hstrat.dataframe.surface_build_tree --help` for details.


Partition Keys
==============
Each `--partition-by` value is evaluated as a Python expression, with access to polars as `pl`.
If evaluation does not produce a polars expression (e.g., a bare column name), the value is taken as a column name.
For example,
    --partition-by 'replicate'
    --partition-by 'pl.col("replicate")'
    --partition-by 'pl.col("update") // 1000'

Pass flag multiple times to partition by combination of values.

Partition key columns are added to input data as with `with_columns`, so name derived keys via `.alias`.
Partition key values are forwarded to all output rows, including inner tree nodes.

To reconstruct separate phylogenies per source data file,
    --with-column 'pl.lit(filepath).alias("source")' --partition-by 'source'


Additional Notes
================
If not provided, 'dstream_data_id' is assigned from row number before partitioning, so values are unique across partitions.
Partitions are ordered by first appearance in input data.
This CLI entrypoint is experimental and may be subject to change.


See Also
========
-m hstrat.dataframe.surface_build_tree :
    Reconstruct a single tree from all genomes.

-m phyloframe.legacy._alifestd_aggregate_phylogeny_partitions_polars :
    Concatenate partitions of a dataframe as independent phylogenies.
"""


def _eval_partition_by(partition_by: str) -> pl.Expr:
    """Evaluate partition key as polars expression, falling back to
    treating it as a column name."""
    try:
        evaluated = eval(partition_by, {"pl": pl})
    except Exception:
        evaluated = None

    if isinstance(evaluated, pl.Expr):
        return evaluated
    else:
        logging.info(f"taking --partition-by {partition_by!r} as column name")
        return pl.col(partition_by)


def _main(mp_context: str) -> None:
    parser = _create_base_parser(
        description=raw_message,
        dfcli_module="hstrat.dataframe.surface_build_tree_over",
    )
    partition_by_action = parser.add_argument(
        "--partition-by",
        action="append",
        default=[],
        dest="partition_by",
        help=(
            "Column name or expression to partition rows by, so that tree "
            "reconstruction is performed independently for each distinct "
            "value (or combination of values, if repeated). Has access to "
            "polars as `pl`. Example: "
            r"""'pl.col("replicate")'"""
        ),
        type=str,
    )
    args, __ = parser.parse_known_args()
    # enforce only in full parse, so that --help works without flag
    partition_by_action.required = True

    partition_by = [*map(_eval_partition_by, args.partition_by)]
    partition_names = [expr.meta.output_name() for expr in partition_by]
    logging.info(f"partitioning by {partition_names}")

    build_tree = _make_build_tree_op(args, mp_context)

    def broadcast_key(
        phylo_df: pl.DataFrame, key: typing.Tuple, schema: pl.Schema
    ) -> pl.DataFrame:
        # forward partition key onto all rows, including inner nodes
        return phylo_df.with_columns(
            pl.lit(value, dtype=schema[name]).alias(name)
            for name, value in zip(partition_names, key)
        )

    with log_context_duration(
        "hstrat.dataframe.surface_build_tree_over", logging.info
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=lambda df: pfl.alifestd_aggregate_phylogeny_partitions_polars(
                pl.concat(
                    [
                        broadcast_key(build_tree(group), key, group.schema)
                        for key, group in tqdm(
                            df.lazy()
                            .with_columns(  # ensure unique across partitions
                                dstream_data_id=pl.coalesce(
                                    pl.col("^dstream_data_id$"),
                                    pl.int_range(pl.len(), dtype=pl.UInt64),
                                ).cast(pl.UInt64),
                            )
                            .with_columns(*partition_by)
                            .collect()
                            .group_by(partition_names, maintain_order=True),
                            desc="partitions",
                        )
                    ]
                    or [build_tree(df.lazy().with_columns(*partition_by))],
                    how="diagonal_relaxed",
                ),
                partitioned_by=partition_names,
            ),
        )


if __name__ == "__main__":
    begin_prod_logging()

    _main("spawn")
