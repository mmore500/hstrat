import argparse
import functools
import logging
import os

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
from tqdm import tqdm

from hstrat.dataframe._surface_test_drive import surface_test_drive

from .._auxiliary_lib import (
    configure_prod_logging,
    format_cli_description,
    get_hstrat_version,
    log_context_duration,
)

raw_message = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Reads alife standard phylogeny dataframe to create a population of hstrat surface annotations corresponding to the phylogeny tips, "as-if" they had evolved according to the provided phylogeny history.

Parameters
----------
df : pl.DataFrame
    The input DataFrame containing alife standard phylogeny with required columns, one row per taxon.

    Note that the alife-standard `ancestor_list` column is not required.

    Required schema:
        - 'id' : pl.UInt64
            - Taxon identifier.
        - 'ancestor_id' : pl.UInt64
            - Taxon identifier of ancestor.
            - Own 'id' if root.

    Optional schema:
        - 'origin_time' : pl.Int64
            - Number of generations elapsed from ancestor.
            - Determines branch lengths.
            - Otherwise, all branches are assumed to be length 1.
        - 'extant' : pl.Boolean
            - Should an entry corresponding to this phylogeny taxon be included in the output population?
            - Otherwise, all tips are considered extant and all inner nodes are not.
        - Additional user-defined columns will be forwarded to the output DataFrame.

dstream_algo : str
    Name of downstream curation algorithm to use.

dstream_S : int
    Capacity of annotation dstream buffer, in number of data items.

stratum_differentia_bit_width : int
    The bit width of the generated differentia.

Returns
-------
pl.DataFrame
    The output DataFrame containing generated hstrat surface annotations.

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
        - 'origin_time' : pl.Int64
            - Number of generations elapsed since the founding ancestor.

    Additional user-defined columns will be forwarded from the input DataFrame.
"""


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        add_help=False,
        description=format_cli_description(raw_message),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    _add_parser_base(
        parser=parser,
        dfcli_module="hstrat.dataframe.surface_test_drive",
        dfcli_version=get_hstrat_version(),
    )
    parser.add_argument(
        "--stratum-differentia-bit-width",
        type=int,
        default=1,
        help="Number of bits used per differentia.",
    )
    parser.add_argument(
        "--dstream-algo",
        type=str,
        default="dstream.tiltedxtc_algo",
        help="Downstream algorithm to curate differentia retention.",
    )
    parser.add_argument(
        "--dstream-S",
        type=int,
        default=64,
        help="Number differentiae to store per surface (usually power of 2).",
    )
    parser.add_argument(
        "--dstream-T-bitwidth",
        type=int,
        default=32,
        help="Number of bits for generation (dstream T) counter.",
    )
    return parser


def _main() -> None:
    parser = _create_parser()
    args, __ = parser.parse_known_args()

    with log_context_duration(
        "hstrat.dataframe.surface_test_drive", logging.info
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=functools.partial(
                surface_test_drive,
                stratum_differentia_bit_width=args.stratum_differentia_bit_width,
                dstream_algo=args.dstream_algo,
                dstream_S=args.dstream_S,
                progress_wrap=tqdm,
            ),
        )


if __name__ == "__main__":
    configure_prod_logging()
    _main()
