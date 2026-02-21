import argparse
import logging
import os
import pathlib
import typing

import numpy as np
import polars as pl
from tqdm import tqdm

from ._alifestd_as_newick_asexual import _build_newick_string
from ._alifestd_has_contiguous_ids_polars import (
    alifestd_has_contiguous_ids_polars,
)
from ._alifestd_is_topologically_sorted_polars import (
    alifestd_is_topologically_sorted_polars,
)
from ._alifestd_try_add_ancestor_id_col_polars import (
    alifestd_try_add_ancestor_id_col_polars,
)
from ._alifestd_unfurl_traversal_postorder_asexual import (
    _alifestd_unfurl_traversal_postorder_asexual_fast_path,
)
from ._configure_prod_logging import configure_prod_logging
from ._eval_kwargs import eval_kwargs
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


def alifestd_as_newick_polars(
    phylogeny_df: pl.DataFrame,
    *,
    taxon_label: typing.Optional[str] = None,
    progress_wrap: typing.Callable = lambda x: x,
) -> str:
    """Convert phylogeny dataframe to Newick format.

    Parameters
    ----------
    phylogeny_df : polars.DataFrame
        Phylogeny dataframe in Alife standard format.
    taxon_label : str, optional
        Column to use for taxon labels, by default None.
    progress_wrap : typing.Callable, optional
        Pass tqdm or equivalent to display a progress bar.

    See Also
    --------
    alifestd_as_newick_asexual :
        Pandas-based implementation.
    """
    logging.info(
        "creating newick string for alifestd polars df",
    )

    if phylogeny_df.lazy().limit(1).collect().is_empty():
        return ";"

    logging.info("adding ancestor id column, if not present")
    phylogeny_df = alifestd_try_add_ancestor_id_col_polars(phylogeny_df)

    schema_names = phylogeny_df.lazy().collect_schema().names()

    if "ancestor_id" not in schema_names:
        raise ValueError("only asexual phylogenies supported")

    if not alifestd_has_contiguous_ids_polars(phylogeny_df):
        raise NotImplementedError("non-contiguous ids not yet supported")

    if not alifestd_is_topologically_sorted_polars(phylogeny_df):
        raise NotImplementedError(
            "polars topological sort not yet implemented",
        )

    ancestor_ids = (
        phylogeny_df.lazy()
        .select(pl.col("ancestor_id").cast(pl.Int64))
        .collect()
        .to_series()
        .to_numpy()
    )
    n = len(ancestor_ids)
    ids = np.arange(n)

    logging.info("setting up `origin_time_delta`...")
    if "origin_time_delta" in schema_names:
        logging.info("... already present!")
        origin_time_deltas = (
            phylogeny_df.lazy()
            .select("origin_time_delta")
            .collect()
            .to_series()
            .to_numpy()
        )
    elif "origin_time" in schema_names:
        logging.info("... calculating from `origin_time`...")
        origin_times = (
            phylogeny_df.lazy()
            .select("origin_time")
            .collect()
            .to_series()
            .to_numpy()
            .astype(float)
        )
        origin_time_deltas = (
            origin_times - origin_times[ancestor_ids.astype(int)]
        )
    else:
        logging.info("... marking null")
        origin_time_deltas = np.full(len(ids), np.nan)

    logging.info("calculating postorder traversal order...")
    postorder_index = _alifestd_unfurl_traversal_postorder_asexual_fast_path(
        ancestor_ids,
    )

    logging.info("preparing labels...")
    if taxon_label is not None:
        labels = (
            phylogeny_df.lazy()
            .select(pl.col(taxon_label).cast(pl.Utf8))
            .collect()
            .to_series()
            .to_numpy()
        )
    else:
        labels = np.full(len(ids), "", dtype=object)

    logging.info("creating newick string...")
    result = _build_newick_string(
        ids[postorder_index],
        labels[postorder_index],
        origin_time_deltas[postorder_index],
        ancestor_ids[postorder_index],
        progress_wrap=progress_wrap,
    )

    logging.info(f"{len(result)=} {result[:20]=}")
    return result


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()})

Convert Alife standard phylogeny data to Newick format, using polars.

Note that this CLI entrypoint is experimental and may be subject to change.
"""


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=format_cli_description(_raw_description),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-i",
        "--input-file",
        type=str,
        help="Alife standard dataframe file to convert to Newick format.",
    )
    parser.add_argument(
        "--input-kwarg",
        action="append",
        dest="input_kwargs",
        type=str,
        default=[],
        help=(
            "Additional keyword arguments to pass to input engine call. "
            "Provide as 'key=value'. "
            "Specify multiple kwargs by using this flag multiple times. "
            "Arguments will be evaluated as Python expressions. "
            "Example: 'infer_schema_length=None'"
        ),
    )
    parser.add_argument(
        "-o",
        "--output-file",
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
    dispatch_reader = {
        ".csv": pl.scan_csv,
        ".fea": pl.scan_ipc,
        ".feather": pl.scan_ipc,
        ".pqt": pl.scan_parquet,
        ".parquet": pl.scan_parquet,
    }

    logging.info(
        f"reading alife-standard {input_ext} phylogeny data from "
        f"{args.input_file}...",
    )
    phylogeny_df = dispatch_reader[input_ext](
        args.input_file,
        **eval_kwargs(args.input_kwargs),
    )

    with log_context_duration(
        "hstrat._auxiliary_lib.alifestd_as_newick_polars", logging.info
    ):
        logging.info("converting to Newick format...")
        newick_str = alifestd_as_newick_polars(
            phylogeny_df, progress_wrap=tqdm, taxon_label=args.taxon_label
        )

    logging.info(f"writing Newick-formatted data to {args.output_file}...")
    pathlib.Path(args.output_file).write_text(newick_str)

    logging.info("done!")
