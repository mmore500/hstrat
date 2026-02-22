import argparse
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
from ._alifestd_validate_trie import alifestd_validate_trie

raw_message = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Validate trie reconstruction output data.

Checks that dstream/downstream columns necessary to deserialize surfaces from data_hex are present, logs the number of tip nodes, and checks that data is topologically sorted with contiguous ids.

Intended for use downstream of `surface_unpack_reconstruct --no-drop-dstream-metadata`.


Input Schema: Required Columns
==============================
'id' : integer
    Unique identifier for each taxon (RE alife standard format).

'ancestor_id' : integer
    Unique identifier for ancestor taxon (RE alife standard format).

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
    Position of dstream counter field ("rank") in 'data_hex'.

'dstream_T_bitwidth' : integer
    Size of dstream counter field in 'data_hex'.

'dstream_S' : integer
    Capacity of dstream buffer, in number of data items (i.e., num differentia stored per annotation).


Additional Notes
================
- Use `--eager-read` if modifying data file inplace.

- This CLI entrypoint is experimental and may be subject to change.


See Also
========
-m hstrat.dataframe.surface_unpack_reconstruct :
    Produces trie reconstruction data validated here.
"""


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        add_help=False,
        description=format_cli_description(raw_message),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    _add_parser_base(
        parser=parser,
        dfcli_module="hstrat.dataframe.alifestd_validate_trie",
        dfcli_version=get_hstrat_version(),
    )
    return parser


if __name__ == "__main__":
    configure_prod_logging()

    parser = _create_parser()
    args, __ = parser.parse_known_args()

    with log_context_duration(
        "hstrat.dataframe.alifestd_validate_trie", logging.info
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=alifestd_validate_trie,
        )
