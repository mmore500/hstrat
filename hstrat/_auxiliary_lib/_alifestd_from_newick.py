import argparse
import logging
import os
import pathlib
import typing

import numpy as np
import pandas as pd
import polars as pl

from ._alifestd_make_ancestor_list_col import alifestd_make_ancestor_list_col
from ._configure_prod_logging import configure_prod_logging
from ._eval_kwargs import eval_kwargs
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._jit import jit
from ._log_context_duration import log_context_duration


@jit(nopython=True)
def _parse_newick(
    chars: np.ndarray,
    n: int,
) -> typing.Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Parse newick string characters into parallel arrays.

    Implementation detail for `alifestd_from_newick`.

    Adapted from
    https://github.com/niemasd/TreeSwift/blob/v1.1.45/treeswift/Tree.py#L1439

    Parameters
    ----------
    chars : np.ndarray
        Array of uint8 character codes for the newick string.
    n : int
        Length of chars array.

    Returns
    -------
    tuple of np.ndarray
        (ids, ancestor_ids, branch_lengths, has_branch_length,
         label_start_stops) where label_start_stops has shape (num_nodes, 2)
        giving the start (inclusive) and stop (exclusive) index into `chars`
        for each node's label.
    """
    # pre-allocate arrays at maximum possible size (n nodes)
    ids = np.empty(n, dtype=np.int64)
    ancestor_ids = np.empty(n, dtype=np.int64)
    branch_lengths = np.empty(n, dtype=np.float64)
    has_branch_length = np.zeros(n, dtype=np.int64)
    label_starts = np.empty(n, dtype=np.int64)
    label_stops = np.empty(n, dtype=np.int64)

    # character codes
    LPAREN = np.uint8(40)  # '('
    RPAREN = np.uint8(41)  # ')'
    COMMA = np.uint8(44)  # ','
    COLON = np.uint8(58)  # ':'
    SEMI = np.uint8(59)  # ';'
    SQUOTE = np.uint8(39)  # "'"
    SPACE = np.uint8(32)  # ' '
    LBRACKET = np.uint8(91)  # '['
    RBRACKET = np.uint8(93)  # ']'

    num_nodes = 0
    # create root node
    root_id = num_nodes
    ids[root_id] = root_id
    ancestor_ids[root_id] = root_id  # root is its own ancestor
    branch_lengths[root_id] = np.nan
    label_starts[root_id] = 0
    label_stops[root_id] = 0
    num_nodes += 1

    cur = root_id
    i = 0
    parse_length = False
    parse_label = False

    while i < n:
        c = chars[i]

        # end of newick string
        if not parse_label and c == SEMI:
            pass  # done

        # go to new child: '('
        elif not parse_label and c == LPAREN:
            child_id = num_nodes
            ids[child_id] = child_id
            ancestor_ids[child_id] = cur
            branch_lengths[child_id] = np.nan
            label_starts[child_id] = 0
            label_stops[child_id] = 0
            num_nodes += 1
            cur = child_id

        # go to parent: ')'
        elif not parse_label and c == RPAREN:
            cur = ancestor_ids[cur]

        # go to new sibling: ','
        elif not parse_label and c == COMMA:
            parent = ancestor_ids[cur]
            child_id = num_nodes
            ids[child_id] = child_id
            ancestor_ids[child_id] = parent
            branch_lengths[child_id] = np.nan
            label_starts[child_id] = 0
            label_stops[child_id] = 0
            num_nodes += 1
            cur = child_id
            # skip spaces after comma
            while i + 1 < n and chars[i + 1] == SPACE:
                i += 1

        # comment (square brackets)
        elif not parse_label and c == LBRACKET:
            count = 1
            i += 1
            while i < n and count > 0:
                if chars[i] == LBRACKET:
                    count += 1
                elif chars[i] == RBRACKET:
                    count -= 1
                i += 1
            i -= 1  # will be incremented at end of loop

        # edge length
        elif not parse_label and c == COLON:
            parse_length = True

        elif parse_length:
            ls_start = i
            while (
                i < n
                and chars[i] != COMMA
                and chars[i] != RPAREN
                and chars[i] != SEMI
                and chars[i] != LBRACKET
            ):
                i += 1
            # parse the accumulated length string
            # manually parse float from chars[ls_start:i]
            length, frac_part, frac_divisor = 0.0, 0.0, 1.0
            is_negative, in_frac, in_exp, exp_neg = False, False, False, False
            exp_val = 0
            j = ls_start
            if j < i and chars[j] == np.uint8(45):  # '-'
                is_negative = True
                j += 1
            if j < i and chars[j] == np.uint8(43):  # '+'
                j += 1
            while j < i:
                ch = chars[j]
                if ch == np.uint8(46):  # '.'
                    in_frac = True
                elif ch == np.uint8(101) or ch == np.uint8(69):  # 'e' or 'E'
                    in_exp = True
                    j += 1
                    if j < i and chars[j] == np.uint8(45):
                        exp_neg = True
                        j += 1
                    elif j < i and chars[j] == np.uint8(43):
                        j += 1
                    continue
                elif in_exp:
                    exp_val = exp_val * 10 + (ch - np.uint8(48))
                elif in_frac:
                    frac_divisor *= 10.0
                    frac_part += (ch - np.uint8(48)) / frac_divisor
                else:
                    length = length * 10.0 + (ch - np.uint8(48))
                j += 1
            length = length + frac_part
            if is_negative:
                length = -length
            if in_exp:
                if exp_neg:
                    length = length / (10.0**exp_val)
                else:
                    length = length * (10.0**exp_val)
            branch_lengths[cur] = length
            has_branch_length[cur] = 1
            i -= 1  # will be incremented at end of loop
            parse_length = False

        # quoted label
        elif not parse_label and c == SQUOTE:
            parse_label = True

        # label (quoted or unquoted)
        else:
            lbl_start = i
            while parse_label or (
                i < n
                and chars[i] != COLON
                and chars[i] != COMMA
                and chars[i] != SEMI
                and chars[i] != RPAREN
                and chars[i] != LBRACKET
            ):
                if chars[i] == SQUOTE:
                    parse_label = not parse_label
                    if not parse_label:
                        i += 1
                        break
                i += 1
            label_starts[cur] = lbl_start
            label_stops[cur] = i
            # strip enclosing quotes from label range if present
            if (
                label_stops[cur] > label_starts[cur]
                and chars[label_starts[cur]] == SQUOTE
            ):
                label_starts[cur] += 1
            if (
                label_stops[cur] > label_starts[cur]
                and chars[label_stops[cur] - 1] == SQUOTE
            ):
                label_stops[cur] -= 1
            parse_label = False
            i -= 1  # will be incremented at end of loop

        i += 1

    # trim to actual size
    ids_out = ids[:num_nodes].copy()
    ancestor_ids_out = ancestor_ids[:num_nodes].copy()
    branch_lengths_out = branch_lengths[:num_nodes].copy()
    has_branch_length_out = has_branch_length[:num_nodes].copy()

    # pack label start/stops into a 2D array
    label_start_stops = np.empty((num_nodes, 2), dtype=np.int64)
    for k in range(num_nodes):
        label_start_stops[k, 0] = label_starts[k]
        label_start_stops[k, 1] = label_stops[k]

    return (
        ids_out,
        ancestor_ids_out,
        branch_lengths_out,
        has_branch_length_out,
        label_start_stops,
    )


def _extract_labels(
    newick: str,
    chars: np.ndarray,
    label_start_stops: np.ndarray,
) -> np.ndarray:
    """Extract taxon labels from newick string using index ranges.

    Implementation detail for `alifestd_from_newick`.
    """
    num_nodes = len(label_start_stops)
    labels = np.empty(num_nodes, dtype=object)
    for k, (start, stop) in enumerate(label_start_stops):
        if start == stop:
            labels[k] = ""
        else:
            label = newick[start:stop]
            # strip enclosing quotes if present
            if len(label) >= 2 and label[0] == "'" and label[-1] == "'":
                label = label[1:-1]
            labels[k] = label
    return labels


def alifestd_from_newick(
    newick: str,
) -> pd.DataFrame:
    """Convert a Newick format string to a phylogeny dataframe.

    Parses a Newick tree string and returns a pandas DataFrame in alife
    standard format with columns: id, ancestor_list, ancestor_id,
    taxon_label, origin_time_delta, and branch_length.

    Parameters
    ----------
    newick : str
        A phylogeny in Newick format.

    Returns
    -------
    pd.DataFrame
        Phylogeny dataframe in alife standard format.

    See Also
    --------
    alifestd_from_newick_polars :
        Polars-based implementation.
    alifestd_as_newick_asexual :
        Inverse conversion, from alife standard to Newick format.
    """
    newick = newick.strip()
    if not newick:
        return pd.DataFrame(
            {
                "id": pd.Series(dtype=int),
                "ancestor_list": pd.Series(dtype=str),
                "ancestor_id": pd.Series(dtype=int),
                "taxon_label": pd.Series(dtype=str),
                "origin_time_delta": pd.Series(dtype=float),
                "branch_length": pd.Series(dtype=float),
            }
        )

    chars = np.frombuffer(newick.encode("ascii"), dtype=np.uint8)
    n = len(chars)

    (
        ids,
        ancestor_ids,
        branch_lengths,
        _,  # has_branch_length
        label_start_stops,
    ) = _parse_newick(chars, n)

    labels = _extract_labels(newick, chars, label_start_stops)

    # build origin_time_delta: same as branch_length for nodes that have it
    origin_time_deltas = branch_lengths.copy()

    phylogeny_df = pd.DataFrame(
        {
            "id": ids,
            "ancestor_id": ancestor_ids,
            "taxon_label": labels,
            "origin_time_delta": origin_time_deltas,
            "branch_length": branch_lengths,
        },
    )

    phylogeny_df["ancestor_list"] = alifestd_make_ancestor_list_col(
        phylogeny_df["id"],
        phylogeny_df["ancestor_id"],
    )

    return phylogeny_df


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()})

Convert Newick format phylogeny data to Alife standard format.

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
        "--output-engine",
        type=str,
        choices=["pandas", "polars"],
        default="pandas",
        help="DataFrame engine to use for writing the output file. Defaults to 'pandas'.",
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
            "Example: 'index=False'"
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
        "hstrat._auxiliary_lib.alifestd_from_newick", logging.info
    ):
        logging.info("converting from Newick format...")
        phylogeny_df = alifestd_from_newick(newick_str)

    output_ext = os.path.splitext(args.output_file)[1]
    dispatch_writer = {
        "pandas+.csv": pd.DataFrame.to_csv,
        "pandas+.fea": pd.DataFrame.to_feather,
        "pandas+.feather": pd.DataFrame.to_feather,
        "pandas+.pqt": pd.DataFrame.to_parquet,
        "pandas+.parquet": pd.DataFrame.to_parquet,
    }

    logging.info(
        f"writing alife-standard {output_ext} phylogeny data to "
        f"{args.output_file}...",
    )
    output_kwargs = eval_kwargs(args.output_kwargs)
    if args.output_engine == "polars":
        phylogeny_df = pl.from_pandas(phylogeny_df)
        dispatch_writer = {
            "polars+.csv": pl.DataFrame.write_csv,
            "polars+.fea": pl.DataFrame.write_ipc,
            "polars+.feather": pl.DataFrame.write_ipc,
            "polars+.pqt": pl.DataFrame.write_parquet,
            "polars+.parquet": pl.DataFrame.write_parquet,
        }
    elif output_ext == ".csv":
        output_kwargs.setdefault("index", False)

    dispatch_writer[f"{args.output_engine}+{output_ext}"](
        phylogeny_df,
        args.output_file,
        **output_kwargs,
    )

    logging.info("done!")
