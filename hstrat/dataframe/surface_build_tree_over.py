import functools
import logging
import os

import joinem
from joinem._dataframe_cli import _eval_kwargs, _run_dataframe_cli
import polars as pl

from .. import hstrat
from .._auxiliary_lib import (
    begin_prod_logging,
    get_hstrat_version,
    log_context_duration,
)
from ._surface_build_tree_over import surface_build_tree_over
from .surface_build_tree import _create_parser as _create_base_parser

raw_message = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Partitioned interface to end-to-end tree reconstruction for surface-based genome annotations.
Splits input rows into partitions by `--partition-by` column(s) or expression(s), and applies `hstrat.dataframe.surface_build_tree` independently to each partition.
Reconstructed phylogenies are then concatenated as independent trees, with taxon ids reassigned to prevent collisions.

Genomes in different partitions are never placed in a shared tree.
All other flags, and input and output schemas, are as for `surface_build_tree`.
See `python3 -m hstrat.dataframe.surface_build_tree --help` for details.


Partition Keys
==============
Provide each `--partition-by` value as 'name=value', where value is a column name (string) or a polars expression.
Values are evaluated as Python expressions, with access to polars as `pl`.
Partition key columns are added to input data as `name`, as with `with_columns`.
For example,
    --partition-by 'replicate="replicate"'
    --partition-by 'replicate=pl.col("replicate")'
    --partition-by 'epoch=pl.col("update") // 1000'

Pass flag multiple times to partition by combination of values.

Partition key values are forwarded to all output rows, including inner tree nodes.

To reconstruct separate phylogenies per source data file,
    --with-column 'pl.lit(filepath).alias("source")' --partition-by 'source="source"'


Additional Notes
================
If not provided, 'dstream_data_id' is assigned from row number before partitioning, so values are unique across partitions.
Partitions are ordered by first appearance in input data.
This CLI entrypoint is experimental and may be subject to change.


See Also
========
-m hstrat.dataframe.surface_build_tree :
    Reconstruct a single tree from all genomes.

hstrat.dataframe.surface_build_tree_over :
    Python API for this CLI entrypoint.

phyloframe.legacy.alifestd_aggregate_phylogenies_polars :
    Concatenate independent phylogenies, reassigning ids.
"""


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
            "Column to partition rows by, so that tree reconstruction is "
            "performed independently for each distinct value (or "
            "combination of values, if repeated). "
            "Provide as 'name=value', where value is a column name or "
            "polars expression. "
            "Arguments will be evaluated as Python expressions, with access "
            "to polars as `pl`. "
            "Example: "
            r"""'epoch=pl.col("update") // 1000'"""
        ),
        type=str,
    )
    args, __ = parser.parse_known_args()
    # enforce only in full parse, so that --help works without flag
    partition_by_action.required = True

    logging.info(
        "instantiating trie postprocess functor: "
        f"`{args.trie_postprocessor}`",
    )
    trie_postprocessor = eval(args.trie_postprocessor, {"hstrat": hstrat})

    with log_context_duration(
        "hstrat.dataframe.surface_build_tree_over", logging.info
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=functools.partial(
                surface_build_tree_over,
                partition_by=[
                    (pl.col(value) if isinstance(value, str) else value).alias(
                        name,
                    )
                    for name, value in _eval_kwargs(args.partition_by).items()
                ],
                collapse_unif_freq=args.collapse_unif_freq,
                check_trie_invariant_freq=args.check_trie_invariant_freq,
                check_trie_invariant_after_collapse_unif=args.check_trie_invariant_after_collapse_unif,
                delete_trunk=args.delete_trunk,
                drop_dstream_metadata=args.drop_dstream_metadata,
                exploded_slice_size=args.exploded_slice_size,
                mp_context=mp_context,
                mp_pool_size=args.mp_pool_size,
                pa_source_type=args.pa_source_type,
                shuffle_over_same_T_seed=args.shuffle_over_same_T_seed,
                trie_postprocessor=trie_postprocessor,
            ),
        )


if __name__ == "__main__":
    begin_prod_logging()

    _main("spawn")
