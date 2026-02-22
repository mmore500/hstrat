import argparse
import logging
import os
from collections import Counter

import pandas as pd

from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


def alifestd_count_unifurcations(phylogeny_df: pd.DataFrame) -> int:
    """Count how many inner nodes have exactly one descendant node.

    Only supports asexual phylogenies.
    """
    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df)
    if "ancestor_id" not in phylogeny_df.columns:
        raise ValueError(
            "alifestd_count_unifurcations only supports asexual phylogenies.",
        )
    except_roots = phylogeny_df["ancestor_id"] != phylogeny_df["id"]
    ancestor_counts = Counter(phylogeny_df.loc[except_roots, "ancestor_id"])
    return sum(v == 1 for v in ancestor_counts.values())


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()})

Print number of unifurcations (non-root nodes with exactly one child) in alife-standard phylogeny.

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
        "hstrat._auxiliary_lib.alifestd_count_unifurcations", logging.info
    ):
        count = alifestd_count_unifurcations(phylogeny_df)

    print(count)

    logging.info("done!")
