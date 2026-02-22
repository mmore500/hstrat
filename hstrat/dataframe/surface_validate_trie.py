import argparse
import logging
import os
import sys

import polars as pl

from .._auxiliary_lib import (
    configure_prod_logging,
    format_cli_description,
    get_hstrat_version,
    log_context_duration,
)
from ._surface_validate_trie import surface_validate_trie

_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()})

Validate trie reconstruction output data.

Performs structural checks and pairwise leaf-node validation to confirm that the trie correctly encodes the hereditary stratigraphic surface data.

Checks performed:
  1. Required dstream/downstream columns for surface deserialization from data_hex are present.
  2. Taxon ids are contiguous (i.e., match row indices 0, 1, ..., n-1).
  3. Data is topologically sorted (each ancestor appears before its descendants).
  4. Samples random leaf-node pairs and compares each pair's first retained
     disparity rank (computed from deserialized surfaces) to the MRCA node's
     dstream_rank - dstream_S in the trie (converting from raw dstream T space
     to hstrat rank space). A violation occurs when
     first_disparity_rank < mrca_rank: the surfaces prove divergence earlier
     than the trie records.

Intended for use after `surface_unpack_reconstruct --no-drop-dstream-metadata`.

Prints the number of detected violations to stdout.
Exits with a non-zero status if structural checks fail or if detected violations exceed --max-violations.


Input Schema: Required Columns
==============================
'id' : integer
    Unique identifier for each taxon (RE alife standard format).

'ancestor_id' : integer
    Unique identifier for ancestor taxon (RE alife standard format).

'dstream_rank' : integer
    Rank stored at this node (number of generations elapsed).

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


See Also
========
-m hstrat.dataframe.surface_unpack_reconstruct :
    Produces trie reconstruction data to be validated here.
"""


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=format_cli_description(_raw_description),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "trie_file",
        type=str,
        help="Trie reconstruction dataframe file to validate (.csv, .pqt, .parquet).",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=get_hstrat_version(),
    )
    parser.add_argument(
        "--max-num-checks",
        type=int,
        default=1_000,
        help=(
            "Maximum number of leaf-pair MRCA comparisons to perform. "
            "Pairs are sampled randomly without replacement. "
            "Default: 1000."
        ),
    )
    parser.add_argument(
        "--max-violations",
        type=int,
        default=1,
        help=(
            "Maximum number of MRCA-rank violations tolerated. "
            "Exits with a non-zero status if detected violations exceed this "
            "threshold. "
            "Default: 1."
        ),
    )
    parser.add_argument(
        "--seed",
        default=None,
        dest="seed",
        help="Integer seed for deterministic behavior.",
        type=int,
    )
    return parser


if __name__ == "__main__":
    configure_prod_logging()

    parser = _create_parser()
    args = parser.parse_args()

    input_ext = os.path.splitext(args.trie_file)[1]
    logging.info(
        f"reading trie reconstruction data from {args.trie_file}...",
    )
    df = {
        ".csv": pl.read_csv,
        ".pqt": pl.read_parquet,
        ".parquet": pl.read_parquet,
    }[input_ext](args.trie_file)

    with log_context_duration(
        "hstrat.dataframe.surface_validate_trie", logging.info
    ):
        num_violations = surface_validate_trie(
            df,
            max_num_checks=args.max_num_checks,
            max_violations=args.max_violations,
            seed=args.seed,
        )

    print(num_violations)

    if num_violations > args.max_violations:
        logging.error(
            "surface_validate_trie: %d violations detected "
            "(exceeds --max-violations %d); exiting with error",
            num_violations,
            args.max_violations,
        )
        sys.exit(1)

    logging.info("done!")
