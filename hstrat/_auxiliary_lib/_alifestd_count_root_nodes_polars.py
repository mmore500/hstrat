import argparse
import logging
import os

import polars as pl

from ._configure_prod_logging import configure_prod_logging
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


def alifestd_count_root_nodes_polars(phylogeny_df: pl.DataFrame) -> int:
    """How many root nodes are contained in phylogeny?"""
    if "ancestor_id" not in phylogeny_df.lazy().collect_schema().names():
        raise NotImplementedError("ancestor_id column required")

    return (
        phylogeny_df.lazy()
        .select((pl.col("id") == pl.col("ancestor_id")).sum())
        .collect()
        .item()
    )


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()})

Print number of root nodes in alife-standard phylogeny.

Note that this CLI entrypoint is experimental and may be subject to change.
"""


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=format_cli_description(_raw_description),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "phylogeny_file",
        type=str,
        help="Alife standard dataframe file to process.",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=get_hstrat_version(),
    )
    return parser


if __name__ == "__main__":
    configure_prod_logging()

    parser = _create_parser()
    args = parser.parse_args()
    input_ext = os.path.splitext(args.phylogeny_file)[1]

    logging.info(
        f"reading alife-standard {input_ext} phylogeny data from "
        f"{args.phylogeny_file}...",
    )
    phylogeny_df = {
        ".csv": pl.read_csv,
        ".fea": pl.read_ipc,
        ".feather": pl.read_ipc,
        ".pqt": pl.read_parquet,
        ".parquet": pl.read_parquet,
    }[input_ext](args.phylogeny_file)

    with log_context_duration(
        "hstrat._auxiliary_lib.alifestd_count_root_nodes_polars", logging.info
    ):
        count = alifestd_count_root_nodes_polars(phylogeny_df)

    print(count)

    logging.info("done!")
