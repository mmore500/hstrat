import argparse
import logging
import os
import pathlib

import numpy as np
import polars as pl

from ._alifestd_from_newick import _extract_labels, _parse_newick
from ._configure_prod_logging import configure_prod_logging
from ._eval_kwargs import eval_kwargs
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


def alifestd_from_newick_polars(
    newick: str,
    *,
    create_ancestor_list: bool = False,
) -> pl.DataFrame:
    """Convert a Newick format string to a phylogeny dataframe.

    Parses a Newick tree string and returns a polars DataFrame in alife
    standard format with columns: id, ancestor_id, taxon_label,
    origin_time_delta, and branch_length. Optionally includes
    ancestor_list.

    Benchmarks on a 200k-node caterpillar tree (JIT-warmed) show
    deserialization ~7x faster than dendropy and comparable to
    treeswift. At 200k nodes: dendropy ~10s vs treeswift ~0.7s.

    Parameters
    ----------
    newick : str
        A phylogeny in Newick format.
    create_ancestor_list : bool, default False
        If True, include an ``ancestor_list`` column in the result.

    Returns
    -------
    pl.DataFrame
        Phylogeny dataframe in alife standard format.

    See Also
    --------
    alifestd_from_newick :
        Pandas-based implementation.
    alifestd_as_newick_asexual :
        Inverse conversion, from alife standard to Newick format.
    """
    newick = newick.strip()
    if not newick:
        columns = {
            "id": pl.Series([], dtype=pl.Int64),
            "ancestor_id": pl.Series([], dtype=pl.Int64),
            "taxon_label": pl.Series([], dtype=pl.Utf8),
            "origin_time_delta": pl.Series([], dtype=pl.Float64),
            "branch_length": pl.Series([], dtype=pl.Float64),
        }
        if create_ancestor_list:
            columns["ancestor_list"] = pl.Series([], dtype=pl.Utf8)
        return pl.DataFrame(columns)

    chars = np.frombuffer(newick.encode("ascii"), dtype=np.uint8)
    n = len(chars)

    (
        ids,
        ancestor_ids,
        branch_lengths,
        _,  # has_branch_length
        label_start_stops,
    ) = _parse_newick(newick, chars, n)

    labels = _extract_labels(newick, chars, label_start_stops)

    origin_time_deltas = branch_lengths.copy()

    columns = {
        "id": pl.Series(ids, dtype=pl.Int64),
        "ancestor_id": pl.Series(ancestor_ids, dtype=pl.Int64),
        "taxon_label": pl.Series(labels.tolist(), dtype=pl.Utf8),
        "origin_time_delta": pl.Series(origin_time_deltas, dtype=pl.Float64),
        "branch_length": pl.Series(branch_lengths, dtype=pl.Float64),
    }

    if create_ancestor_list:
        ancestor_list = []
        for id_, anc_id in zip(ids, ancestor_ids):
            if id_ == anc_id:
                ancestor_list.append("[none]")
            else:
                ancestor_list.append(f"[{anc_id}]")
        columns["ancestor_list"] = pl.Series(ancestor_list, dtype=pl.Utf8)

    return pl.DataFrame(columns)


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()})

Convert Newick format phylogeny data to Alife standard format (Polars).

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
        help="Newick file to convert to Alife standard dataframe format.",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        type=str,
        help="Path to write Alife standard dataframe output to.",
    )
    parser.add_argument(
        "--output-kwarg",
        action="append",
        dest="output_kwargs",
        type=str,
        default=[],
        help=(
            "Additional keyword arguments to pass to output engine call. "
            "Provide as 'key=value'. "
            "Specify multiple kwargs by using this flag multiple times. "
            "Arguments will be evaluated as Python expressions. "
            "Example: 'include_header=False'"
        ),
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

    logging.info(f"reading Newick data from {args.input_file}...")
    newick_str = pathlib.Path(args.input_file).read_text()

    with log_context_duration(
        "hstrat._auxiliary_lib.alifestd_from_newick_polars", logging.info
    ):
        logging.info("converting from Newick format...")
        phylogeny_df = alifestd_from_newick_polars(newick_str)

    output_ext = os.path.splitext(args.output_file)[1]
    dispatch_writer = {
        ".csv": pl.DataFrame.write_csv,
        ".fea": pl.DataFrame.write_ipc,
        ".feather": pl.DataFrame.write_ipc,
        ".pqt": pl.DataFrame.write_parquet,
        ".parquet": pl.DataFrame.write_parquet,
    }

    logging.info(
        f"writing alife-standard {output_ext} phylogeny data to "
        f"{args.output_file}...",
    )
    dispatch_writer[output_ext](
        phylogeny_df,
        args.output_file,
        **eval_kwargs(args.output_kwargs),
    )

    logging.info("done!")
