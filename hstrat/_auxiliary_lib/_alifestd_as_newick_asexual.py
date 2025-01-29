import argparse
import logging
import os
import pathlib
import typing

import more_itertools as mit
import numpy as np
import opytional as opyt
import pandas as pd
from tqdm import tqdm

from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_mark_origin_time_delta_asexual import (
    alifestd_mark_origin_time_delta_asexual,
)
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._alifestd_unfurl_traversal_postorder_asexual import (
    alifestd_unfurl_traversal_postorder_asexual,
)
from ._configure_prod_logging import configure_prod_logging
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration

# adapted from https://stackoverflow.com/a/3939381/17332200
_UNSAFE_SYMBOLS = ";(),[]:'"
_UNSAFE_TRANSLATION_TABLE = str.maketrans("", "", _UNSAFE_SYMBOLS)


def _format_newick_repr(taxon_label: str, origin_time_delta: str) -> str:
    # adapted from https://github.com/niemasd/TreeSwift/blob/63b8979fb5e616ba89079d44e594682683c1365e/treeswift/Node.py#L129
    label = taxon_label

    if label.translate(_UNSAFE_TRANSLATION_TABLE) != label:
        label = label.join("''")

    if origin_time_delta != "nan":
        if "." in origin_time_delta:
            origin_time_delta = origin_time_delta.rstrip("0").rstrip(".")
        label = f"{label}:{origin_time_delta}"

    return label


def _build_newick_string(
    ids: np.ndarray,
    labels: np.ndarray,
    origin_time_deltas: np.ndarray,
    ancestor_ids: np.ndarray,
    *,
    progress_wrap: typing.Callable,
) -> str:
    child_newick_reprs = dict()
    for id_, taxon_label, origin_time_delta, ancestor_id in progress_wrap(
        zip(ids, labels, origin_time_deltas, ancestor_ids)
    ):
        newick_repr = _format_newick_repr(taxon_label, origin_time_delta)

        children_reprs = child_newick_reprs.pop(id_, None)
        if children_reprs is not None:
            newick_repr = f"({','.join(children_reprs)}){newick_repr}"

        child_newick_reprs.setdefault(ancestor_id, []).append(newick_repr)

    logging.info(f"finalizing {len(child_newick_reprs)} subtrees...")
    return ";\n".join(map(mit.one, child_newick_reprs.values())) + ";"


def alifestd_as_newick_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
    *,
    taxon_label: typing.Optional[str] = None,
    progress_wrap=lambda x: x,
) -> str:
    """Convert phylogeny dataframe to Newick format.

    Parameters
    ----------
    phylogeny_df : pd.DataFrame
        Phylogeny dataframe in Alife standard format.
    mutate : bool, optional
        Allow in-place mutations of the input dataframe, by default False.
    taxon_label : str, optional
        Column to use for taxon labels, by default None.
    progress_wrap : typing.Callable, optional
        Pass tqdm or equivalent to display a progress bar.
    """

    logging.info(
        "creating newick string for alifestd df "
        f"with shape {phylogeny_df.shape}",
    )

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    logging.info("adding ancestor id column, if not present")
    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    if alifestd_has_contiguous_ids(phylogeny_df):
        phylogeny_df.reset_index(drop=True, inplace=True)
    else:
        phylogeny_df.index = phylogeny_df["id"]

    logging.info("setting up `origin_time_delta` column...")
    if "origin_time_delta" in phylogeny_df.columns:
        logging.info("... already present!")
    elif "origin_time" in phylogeny_df.columns:
        logging.info("... calculating from `origin_time`...")
        phylogeny_df = alifestd_mark_origin_time_delta_asexual(
            phylogeny_df, mutate=True
        )
    else:
        logging.info("... marking null")
        phylogeny_df["origin_time_delta"] = np.nan

    logging.info("calculating postorder traversal order...")
    postorder_ids = alifestd_unfurl_traversal_postorder_asexual(phylogeny_df)

    logging.info("preparing labels...")
    phylogeny_df["__hstrat_label"] = opyt.apply_if_or_value(
        taxon_label, phylogeny_df.__getitem__, ""
    )
    phylogeny_df["__hstrat_label"] = phylogeny_df["__hstrat_label"].astype(str)

    logging.info("reshaping data...")
    reshaped = (
        phylogeny_df.loc[
            postorder_ids,
            ["id", "__hstrat_label", "origin_time_delta", "ancestor_id"],
        ]
        .astype({"origin_time_delta": str})
        .to_numpy()
        .T
    )

    logging.info("creating newick string...")
    result = _build_newick_string(*reshaped, progress_wrap=progress_wrap)

    logging.info(f"{len(result)=} {result[:20]=}")
    return result


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()})

Convert Alife standard phylogeny data to Newick format.

Note that this CLI entrypoint is experimental and may be subject to change.
"""


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=format_cli_description(_raw_description),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--input-file",
        "-i",
        type=str,
        help="Alife standard dataframe file to convert to Newick format.",
    )
    parser.add_argument(
        "--output-file",
        "-o",
        type=str,
        help="Path to write Newick-formatted output to.",
    )
    parser.add_argument(
        "-l",
        "--taxon-label",
        type=str,
        help="Name of column to use as taxon label.",
        required=False,
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
    input_ext = os.path.splitext(args.input_file)[1]

    logging.info(
        f"reading alife-standard {input_ext} phylogeny data from "
        f"{args.input_file}...",
    )
    phylogeny_df = {
        ".csv": pd.read_csv,
        ".fea": pd.read_feather,
        ".feather": pd.read_feather,
        ".pqt": pd.read_parquet,
        ".parquet": pd.read_parquet,
    }[input_ext](args.input_file)

    with log_context_duration(
        "hstrat._auxiliary_lib.alifestd_as_newick_asexual", logging.info
    ):
        logging.info("converting to Newick format...")
        newick_str = alifestd_as_newick_asexual(
            phylogeny_df, progress_wrap=tqdm, taxon_label=args.taxon_label
        )

    logging.info(f"writing Newick-formatted data to {args.output_file}...")
    pathlib.Path(args.output_file).write_text(newick_str)

    logging.info("done!")
