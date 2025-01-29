import argparse
import functools
import logging
import os

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli

from .._auxiliary_lib import (
    configure_prod_logging,
    format_cli_description,
    get_hstrat_version,
    log_context_duration,
)
from ._surface_unpack_reconstruct import surface_unpack_reconstruct

raw_message = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

First component of raw interface to tree reconstruction for surface-based genome annotations.
Reads raw genome data from tabular data file(s) and writes reconstructed phylogeny data to output file in alife standard format.


End-users are recommended to prefer `hstrat.dataframe.surface_build_tree`.
Performs no post-processing operations, including taxon `origin_time` estimation.
Surface-only implementation --- not compatible with HereditaryStratigraphicColumn genome annotations.


Input Schema: Required Columns
==============================
'data_hex' : string
    Raw genome data, with serialized dstream buffer and counter.
    Represented as a hexadecimal string.

'dstream_algo' : string or categorical
    Name of downstream curation algorithm used (e.g., 'dstream.steady_algo').

'dstream_storage_bitoffset' : integer
    Position of dstream buffer field in 'data_hex'.

'dstream_storage_bitwidth' : integer
    Size of dstream buffer field in 'data_hex'.

'dstream_T_bitoffset' : integer
    Position of dstream counter field ("rank”) in 'data_hex'.

'dstream_T_bitwidth' : integer
    Size of dstream counter field in 'data_hex'.

'dstream_S' : integer
    Capacity of dstream buffer, in number of data items (i.e., num differentia stored per annotation).


If required columns are not included in raw data, they must be created through CLI flags.
For example,
    --with-column 'pl.lit("dstream.tilted_algo").alias("dstream_algo").cast(pl.Categorical)'”
    --with-column 'pl.lit("genome_string").alias("data_hex")'


Input Schema: Optional Columns
==============================
'downstream_version' : string or categorical
    Version of downstream library used to curate annotation data.

'dstream_data_id' : integer
    Unique identifier for each data item. Will be set automatically if not provided.


Additional user-provided columns will be forwarded to phylogeny output.
For these columns, output rows for tip nodes are assigned values from corresponding genome row in original data.
Internal tree nodes will take null values in user-provided columns.


Output Schema
=============
'id' : integer
    Unique identifier for each taxon (RE alife standard format).

'ancestor_id' : integer
    Unique identifier for ancestor taxon (RE alife standard format).

'hstrat_rank' : floating point or integer
    Num generations elapsed for ancestral differentia (a.k.a. rank).
    Corresponds to `dstream_Tbar` for inner nodes.
    Corresponds `dstream_T` - 1 for leaf nodes.

'differentia_bitwidth' : integer
    Size of annotation differentiae, in bits.
    Corresponds to `dstream_value_bitwidth`.

'dstream_data_id' : integer
    Unique identifier for each genome in source dataframe.
    Set to source dataframe row index if not provided by end user.

'dstream_S' : pl.UInt32
    Capacity of dstream buffer used for hstrat surface, in number of data items (i.e., differentia values).


See Also
========
-m hstrat.dataframe.surface_postprocess_trie :
    Post-processes raw phylogeny data, including collapsing superfluous internal nodes and estimating taxon origin times.

-m hstrat._auxiliary_lib._alifestd_try_add_ancestor_list_col :
    Adds alife-standard `ancestor_list` column to phylogeny data.


Additional Notes
================
Behind the scenes, the following processing steps occur:
1. Data is loaded from user-provided tabular data file(s), with format inferred from filename extension (if not explicitly provided).

2. Any data transformations from CLI flags and arguments are applied.

3. Annotation data (i.e., downstream buffer and counter components of hstrat surface) are extracted from raw genome fields.
For details, see `python3 -m downstream.dataframe.unpack_data_packed --help`.

4. Differentia are unpacked from downstream buffer and data item origin times are decoded from generation counter and buffer size.
For details, see `python3 -m downstream.dataframe.explode_lookup_unpacked --help`.

5. A trie-based algorithm is used to reconstruct an estimate of phylogenetic history from annotation data.

6. Reconstructed phylogeny data is joined with user-provided columns from original data files.

7. Phylogeny data is saved in alife standard format to user-specified output file, with file type inferred from filename extension (if not explicitly provided).


To streamline memory and disk usage, consider using CLI flags to cast string columns with repeated data values to categorical, shrink data types, or drop superfluous columns.
The `--exploded-slice-size` flag may also be used to control memory usage during trie reconstruction.
Dataframe operations are conducted using polars and downstream operations may employ numba, both of which are capable of thread-based parallelism.
Environment variables POLARS_MAX_THREADS and NUMBA_NUM_THREADS may be used to tune thread usage.
"""


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        add_help=False,
        description=format_cli_description(raw_message),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    _add_parser_base(
        parser=parser,
        dfcli_module="hstrat.dataframe.surface_unpack_reconstruct",
        dfcli_version=get_hstrat_version(),
    )
    parser.add_argument(
        "--collapse-unif-freq",
        type=int,
        default=1,
        help="How often should dropped unifurcations be garbage collected?",
    )
    parser.add_argument(
        "--exploded-slice-size",
        type=int,
        default=1_000_000,
        help="Number of rows to process at once. Low values reduce memory use.",
    )
    return parser


def _main(mp_context: str) -> None:
    parser = _create_parser()
    args, __ = parser.parse_known_args()

    with log_context_duration(
        "hstrat.dataframe.surface_unpack_reconstruct", logging.info
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=functools.partial(
                surface_unpack_reconstruct,
                collapse_unif_freq=args.collapse_unif_freq,
                exploded_slice_size=args.exploded_slice_size,
                mp_context=mp_context,
            ),
        )


if __name__ == "__main__":
    configure_prod_logging()
    _main("spawn")
