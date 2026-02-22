import argparse
import logging
import os

import pandas as pd

from ._alifestd_mark_num_children_asexual import (
    alifestd_mark_num_children_asexual,
)
from ._alifestd_mark_roots import alifestd_mark_roots
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


def alifestd_count_unifurcating_roots_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> int:
    """How many root nodes with one child are contained in phylogeny?"""

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_mark_num_children_asexual(
        phylogeny_df, mutate=True
    )
    phylogeny_df = alifestd_mark_roots(phylogeny_df, mutate=True)

    return (
        phylogeny_df["is_root"] & (phylogeny_df["num_children"] == 1)
    ).sum()


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()})

Print number of unifurcating root nodes in alife-standard phylogeny.

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
    parser = _create_parser()
    args = parser.parse_args()
    input_ext = os.path.splitext(args.phylogeny_file)[1]

    logging.info(
        f"reading alife-standard {input_ext} phylogeny data from "
        f"{args.phylogeny_file}...",
    )
    phylogeny_df = {
        ".csv": pd.read_csv,
        ".fea": pd.read_feather,
        ".feather": pd.read_feather,
        ".pqt": pd.read_parquet,
        ".parquet": pd.read_parquet,
    }[input_ext](args.phylogeny_file)

    with log_context_duration(
        "hstrat._auxiliary_lib.alifestd_count_unifurcating_roots_asexual",
        logging.info,
    ):
        count = alifestd_count_unifurcating_roots_asexual(phylogeny_df)

    print(count)

    logging.info("done!")
