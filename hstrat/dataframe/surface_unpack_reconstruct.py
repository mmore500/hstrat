import argparse
import functools
import logging
import textwrap

from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli

from .._auxiliary_lib import (
    collapse_nonleading_whitespace,
    get_hstrat_version,
    join_paragraphs_from_one_sentence_per_line,
    log_context_duration,
    textwrap_respect_indents,
)
from ._surface_unpack_reconstruct import surface_unpack_reconstruct

raw_message = """Raw interface to tree reconstruction for surface-based genome annotations.
Reads raw genome data from tabular data file(s) and writes reconstructed phylogeny data to output file in alife standard format.


End-users are recommended to prefer `hstrat.dataframe.build_tree`.
Uses naive method to estimate taxon `origin_time`s and performs no post-processing operations.
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
'taxon_id' : integer
    Unique identifier for each taxon (RE alife standard format).

'ancestor_id' : integer
    Unique identifier for ancestor taxon (RE alife standard format).

'ancestor_list' : string
    List of ancestor taxon identifiers (RE alife standard format).

'origin_time' : floating point or integer
    Num generations elapsed for ancestral differentia (a.k.a. rank), RE alife standard format.
    Corresponds to `dstream_Tbar` for inner nodes.
    Corresponds `dstream_T` - 1 for leaf nodes.

'differentia_bitwidth' : integer
    Size of annotation differentiae, in bits.
    Corresponds to `dstream_value_bitwidth`.

'dstream_data_id' : integer
    Unique identifier for each genome in source dataframe.
    Set to source dataframe row index if not provided by end user.


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
Dataframe operations are conducted using polars and downstream operations may employ numba, both of which are capable of thread-based parallelism.
Environment variables POLARS_MAX_THREADS and NUMBA_NUM_THREADS may be used to tune thread usage.
"""


def _format_message(message: str) -> str:
    """Fix whitespace to pretty-print description message on CLI."""
    message = join_paragraphs_from_one_sentence_per_line(message)
    message = collapse_nonleading_whitespace(message)
    message = textwrap_respect_indents(message)
    message = textwrap.indent(message, prefix="  ")
    return message


if __name__ == "__main__":
    logging.basicConfig(
        datefmt="%Y-%m-%d %H:%M:%S",
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
    )
    parser = argparse.ArgumentParser(
        description=_format_message(raw_message),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    _add_parser_base(
        parser=parser,
        dfcli_module="hstrat.dataframe.surface_unpack_reconstruct",
        dfcli_version=get_hstrat_version(),
    )
    parser.add_argument(
        "--exploded-slice-size",
        type=int,
        default=1_000_000,
        help="Number of rows to process at once. Low values reduce memory use.",
    )
    args, __ = parser.parse_known_args()

    with log_context_duration(
        "end-to-end surface_unpack_reconstruct", logging.info
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=functools.partial(
                surface_unpack_reconstruct,
                exploded_slice_size=args.exploded_slice_size,
            ),
        )
