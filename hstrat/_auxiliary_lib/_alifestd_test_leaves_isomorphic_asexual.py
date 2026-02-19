import argparse
import logging
import os
import sys

import pandas as pd
from tqdm import tqdm

from ._alifestd_collapse_unifurcations import alifestd_collapse_unifurcations
from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_mark_leaves import alifestd_mark_leaves
from ._alifestd_to_working_format import alifestd_to_working_format
from ._configure_prod_logging import configure_prod_logging
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


def alifestd_test_leaves_isomorphic_asexual(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    taxon_label: str,
    mutate: bool = False,
    progress_wrap: callable = lambda x: x,
) -> bool:
    """Test if phylogenetic relationships between leaf nodes are topologically
    isomorphic between two phylogenies."""

    if not mutate:
        df1, df2 = df1.copy(), df2.copy()

    if taxon_label == "id":
        df1["taxon_label"], df2["taxon_label"] = df1["id"], df2["id"]
        taxon_label = "taxon_label"

    df1 = alifestd_to_working_format(df1, mutate=True)
    df2 = alifestd_to_working_format(df2, mutate=True)

    df1 = alifestd_collapse_unifurcations(df1, mutate=True)
    df2 = alifestd_collapse_unifurcations(df2, mutate=True)

    df1 = alifestd_to_working_format(df1, mutate=True)
    df2 = alifestd_to_working_format(df2, mutate=True)

    df1 = alifestd_mark_leaves(df1, mutate=True)
    df2 = alifestd_mark_leaves(df2, mutate=True)

    df1, df2 = df1.reset_index(drop=True), df2.reset_index(drop=True)
    assert alifestd_has_contiguous_ids(df1)
    assert alifestd_has_contiguous_ids(df2)

    if len(df1) != len(df2):
        return False

    leaves1, leaves2 = df1[df1["is_leaf"]], df2[df2["is_leaf"]]

    if set(leaves1[taxon_label]) != set(leaves2[taxon_label]):
        return False

    df2_id_lookup = dict(zip(leaves2[taxon_label], leaves2["id"]))
    id_map = dict(zip(leaves1["id"], leaves1[taxon_label].map(df2_id_lookup)))

    for id1 in progress_wrap(df1["id"][::-1]):
        assert id1 in id_map
        ancestor_id1 = df1["ancestor_id"].iat[id1]

        id2 = id_map[id1]
        ancestor_id2 = df2["ancestor_id"].iat[id2]

        if ancestor_id1 in id_map:
            if id_map[ancestor_id1] != ancestor_id2:
                return False
        else:
            id_map[ancestor_id1] = ancestor_id2

    return True


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()})

Test if phylogenetic relationships between leaf nodes are topologically
isomorphic between two phylogenies.

Return code 0 indicates isomorphism; 1 indicates non-isomorphism.

Note that this CLI entrypoint is experimental and may be subject to change.
"""


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=format_cli_description(_raw_description),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "first_phylogeny",
        type=str,
        help="Path to first alife-standard phylogeny file",
    )
    parser.add_argument(
        "second_phylogeny",
        type=str,
        help="Path to second alife-standard phylogeny file",
    )
    parser.add_argument(
        "-l",
        "--taxon-label",
        type=str,
        help="Name of column to use as taxon label.",
        required=True,
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
    input_ext = [1]

    logging.info(f"reading first phylogeny from {args.first_phylogeny}...")
    first_df = {
        ".csv": pd.read_csv,
        ".fea": pd.read_feather,
        ".feather": pd.read_feather,
        ".pqt": pd.read_parquet,
        ".parquet": pd.read_parquet,
    }[os.path.splitext(args.first_phylogeny)[1]](args.first_phylogeny)

    logging.info(f"reading second phylogeny from {args.second_phylogeny}...")
    second_df = {
        ".csv": pd.read_csv,
        ".fea": pd.read_feather,
        ".feather": pd.read_feather,
        ".pqt": pd.read_parquet,
        ".parquet": pd.read_parquet,
    }[os.path.splitext(args.second_phylogeny)[1]](args.second_phylogeny)

    with log_context_duration(
        "hstrat._auxiliary_lib.alifestd_test_leaves_isomorphic_asexual",
        logging.info,
    ):
        result = alifestd_test_leaves_isomorphic_asexual(
            first_df,
            second_df,
            taxon_label=args.taxon_label,
            progress_wrap=tqdm,
        )

    exit_code = [1, 0][result]

    logging.info(f"exiting with return code {exit_code} for result {result}")
    sys.exit(exit_code)
