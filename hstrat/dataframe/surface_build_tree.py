import argparse
import functools
import logging
import os

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli

from .. import hstrat
from .._auxiliary_lib import (
    configure_prod_logging,
    format_cli_description,
    get_hstrat_version,
    log_context_duration,
)
from ._surface_build_tree import surface_build_tree

raw_message = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

End-to-end interface to tree reconstruction for surface-based genome annotations.
Reads raw hex genome data from tabular data file(s) and writes postprocessed phylogeny data to output file in alife standard format.


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


Additional user-provided columns will be forwarded to phylogeny output.
For these columns, output rows for tip nodes are assigned values from corresponding genome row in original data.


Output Schema: Required Columns
===============================
'id' : integer
    Unique identifier for each taxon (RE alife standard format).
    Will be reassigned for contiguity and may differ from input.

'ancestor_id' : integer
    Unique identifier for ancestor taxon (RE alife standard format).

'hstrat_rank_from_t0' : integer
    - Num generations elapsed for ancestral differentia.
    - Corresponds to `dstream_Tbar` - `dstream_S` for inner nodes.
    - Corresponds `dstream_T` - 1 - `dstream_S` for leaf nodes


Output Schema: Optional Columns
===============================
'origin_time' : floating point or integer
    Estimated num generations elapsed from founding ancestor.
    Value depends on the trie postprocessor used.

Additional user-defined columns will be forwarded from the input DataFrame.
Note that the alife-standard `ancestor_list` column is not included in output schema.


See Also
========
-m hstrat.dataframe.surface_unpack_reconstrct :
-m hstrat.dataframe.surface_postprocess_trie :
    Low-level CLI interface for phylogeny reconstruction.
    See their docstrings/help messages for technical details on reconstruction
    and postprocessing operations.

-m hstrat._auxiliary_lib._alifestd_try_add_ancestor_list_col :
    Adds alife-standard `ancestor_list` column to phylogeny data.
"""


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        add_help=False,
        description=format_cli_description(raw_message),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    _add_parser_base(
        parser=parser,
        dfcli_module="hstrat.dataframe.surface_build_tree",
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
    parser.add_argument(
        "--delete-trunk",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=(
            "Should trunk nodes with rank less than `dstream_S` be deleted? "
            "Trunk deletion accounts for 'dummy' strata added to fill hstrat "
            "surface for founding ancestor(s), by segregating subtrees with "
            "distinct founding strata into independent trees."
        ),
    )
    parser.add_argument(
        "--trie-postprocessor",
        type=str,
        default="hstrat.NopTriePostprocessor()",
        help=(
            "Functor to apply to finalize postprocessed phylogeny. "
            "Postprocessors are available to estimate taxon `origin_time`, "
            "apply topological corrections for systematic overestimation of "
            "relatedness, etc. "
            "Will be `eval`-ed as Python code before use."
            "Must support Pandas dataframe input."
        ),
    )
    return parser


def _main(mp_context: str) -> None:
    parser = _create_parser()
    args, __ = parser.parse_known_args()

    logging.info(
        "instantiating trie postprocess functor: "
        f"`{args.trie_postprocessor}`",
    )
    trie_postprocessor = eval(args.trie_postprocessor, {"hstrat": hstrat})

    with log_context_duration(
        "hstrat.dataframe.surface_build_tree", logging.info
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=functools.partial(
                surface_build_tree,
                collapse_unif_freq=args.collapse_unif_freq,
                delete_trunk=args.delete_trunk,
                exploded_slice_size=args.exploded_slice_size,
                mp_context=mp_context,
                trie_postprocessor=trie_postprocessor,
            ),
        )


if __name__ == "__main__":
    configure_prod_logging()

    _main("spawn")
