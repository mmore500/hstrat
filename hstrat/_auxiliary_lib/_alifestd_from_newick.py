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
def _parse_newick_jit(
    chars: np.ndarray,
    n: int,
) -> typing.Tuple[
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    int,
    int,
]:
    """Inner JIT kernel for newick parsing.

    Allocates and populates arrays with tree structure and records
    branch-length substring positions for external float conversion.

    Implementation detail for `_parse_newick`.

    Adapted from
    https://github.com/niemasd/TreeSwift/blob/v1.1.45/treeswift/Tree.py#L1439

    Returns
    -------
    tuple
        (ids, ancestor_ids, label_starts, label_stops, bl_starts, bl_stops,
         bl_node_ids, num_nodes, num_bls).
    """
    # estimate max node count using a translation table: each '(' and ','
    # creates a node, plus the root
    node_weight = np.zeros(256, dtype=np.int64)
    node_weight[np.uint8(ord(","))] = 1
    node_weight[np.uint8(ord("("))] = 1
    max_nodes = 1 + np.sum(node_weight[chars])

    # pre-allocate arrays using heuristic size
    ids = np.empty(max_nodes, dtype=np.int64)
    ancestor_ids = np.empty(max_nodes, dtype=np.int64)
    label_starts = np.zeros(max_nodes, dtype=np.int64)
    label_stops = np.zeros(max_nodes, dtype=np.int64)
    bl_starts = np.empty(max_nodes, dtype=np.int64)
    bl_stops = np.empty(max_nodes, dtype=np.int64)
    bl_node_ids = np.empty(max_nodes, dtype=np.int64)

    # character codes
    LPAREN = np.uint8(ord("("))
    RPAREN = np.uint8(ord(")"))
    COMMA = np.uint8(ord(","))
    COLON = np.uint8(ord(":"))
    SEMI = np.uint8(ord(";"))
    SQUOTE = np.uint8(ord("'"))
    SPACE = np.uint8(ord(" "))
    LBRACKET = np.uint8(ord("["))
    RBRACKET = np.uint8(ord("]"))

    # translation tables for delimiter detection
    is_bl_term = np.zeros(256, dtype=np.uint8)
    is_bl_term[COMMA] = 1
    is_bl_term[RPAREN] = 1
    is_bl_term[SEMI] = 1
    is_bl_term[LBRACKET] = 1

    is_lbl_term = np.zeros(256, dtype=np.uint8)
    is_lbl_term[COLON] = 1
    is_lbl_term[COMMA] = 1
    is_lbl_term[SEMI] = 1
    is_lbl_term[RPAREN] = 1
    is_lbl_term[LBRACKET] = 1

    # create root node (id 0)
    ids[0] = 0
    ancestor_ids[0] = 0  # root is its own ancestor
    num_nodes = 1
    num_bls = 0

    cur = 0
    i = 0

    while i < n:
        c = chars[i]

        # go to new child: '(' — most frequent structural characters first
        if c == LPAREN:
            child_id = num_nodes
            ids[child_id] = child_id
            ancestor_ids[child_id] = cur
            num_nodes += 1
            cur = child_id

        # go to new sibling: ','
        elif c == COMMA:
            parent = ancestor_ids[cur]
            child_id = num_nodes
            ids[child_id] = child_id
            ancestor_ids[child_id] = parent
            num_nodes += 1
            cur = child_id
            # skip spaces after comma
            while i + 1 < n and chars[i + 1] == SPACE:
                i += 1

        # go to parent: ')'
        elif c == RPAREN:
            cur = ancestor_ids[cur]

        # edge length — parse immediately without re-entering loop
        elif c == COLON:
            i += 1
            ls_start = i
            while i < n and not is_bl_term[chars[i]]:
                i += 1
            bl_starts[num_bls] = ls_start
            bl_stops[num_bls] = i
            bl_node_ids[num_bls] = cur
            num_bls += 1
            i -= 1  # will be incremented at end of loop

        # quoted label — parse inline through closing quote
        elif c == SQUOTE:
            i += 1
            lbl_start = i
            while i < n and chars[i] != SQUOTE:
                i += 1
            label_starts[cur] = lbl_start
            label_stops[cur] = i
            # i now points at closing quote; will be incremented at end

        # comment (square brackets)
        elif c == LBRACKET:
            count = 1
            i += 1
            while i < n and count > 0:
                count += chars[i] == LBRACKET
                count -= chars[i] == RBRACKET
                i += 1
            i -= 1  # will be incremented at end of loop

        # end of newick string
        elif c == SEMI:
            pass

        # unquoted label
        else:
            lbl_start = i
            while i < n and not is_lbl_term[chars[i]]:
                i += 1
            label_starts[cur] = lbl_start
            label_stops[cur] = i
            i -= 1  # will be incremented at end of loop

        i += 1

    return (
        ids,
        ancestor_ids,
        label_starts,
        label_stops,
        bl_starts,
        bl_stops,
        bl_node_ids,
        num_nodes,
        num_bls,
    )


def _parse_newick(
    newick: str,
    chars: np.ndarray,
    n: int,
    branch_length_dtype: type = float,
) -> typing.Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Parse newick string characters into parallel arrays.

    Implementation detail for `alifestd_from_newick`.

    Uses a two-phase approach: an inner numba JIT kernel handles structural
    parsing and records branch-length substring positions, then float
    conversion is performed externally via numpy.

    Adapted from
    https://github.com/niemasd/TreeSwift/blob/v1.1.45/treeswift/Tree.py#L1439

    Parameters
    ----------
    newick : str
        The newick string (used for substring extraction).
    chars : np.ndarray
        Array of uint8 character codes for the newick string.
    n : int
        Length of chars array.
    branch_length_dtype : type, default float
        Dtype for branch length parsing. Strings are converted via this
        dtype (providing validation), then stored as float64 with NaN for
        missing values. Callers handle nullable-int conversion.

    Returns
    -------
    tuple of np.ndarray
        (ids, ancestor_ids, branch_lengths, label_start_stops) where
        branch_lengths is float64 with NaN for missing values (callers
        should convert to nullable int if needed), and label_start_stops
        has shape (num_nodes, 2) giving the start (inclusive) and stop
        (exclusive) index into `chars` for each node's label.
    """
    (
        ids,
        ancestor_ids,
        label_starts,
        label_stops,
        bl_starts,
        bl_stops,
        bl_node_ids,
        num_nodes,
        num_bls,
    ) = _parse_newick_jit(chars, n)

    # trim to actual sizes
    ids = ids[:num_nodes]
    ancestor_ids = ancestor_ids[:num_nodes]

    # branch lengths: parse substrings using the requested dtype, then
    # store as float64 (to support NaN for missing values)
    np_dtype = np.dtype(branch_length_dtype)
    branch_lengths = np.full(num_nodes, np.nan, dtype=np.float64)
    if num_bls:
        # string extraction is sequential (variable-length slices);
        # numeric conversion is vectorized via np.array
        node_ids = bl_node_ids[:num_bls]
        starts = bl_starts[:num_bls]
        stops = bl_stops[:num_bls]
        bl_strings = [newick[starts[k] : stops[k]] for k in range(num_bls)]
        branch_lengths[node_ids] = np.array(bl_strings, dtype=np_dtype)

    # pack label start/stops into a 2D array
    label_start_stops = np.column_stack(
        (label_starts[:num_nodes], label_stops[:num_nodes])
    )

    return (
        ids,
        ancestor_ids,
        branch_lengths,
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
            labels[k] = newick[start:stop].strip("'")
    return labels


# Performance (as of 2026-03-01, 200k-node caterpillar tree, JIT-warmed):
#   with branch lengths: hstrat ~0.9s vs treeswift ~1.1s (~0.8x)
#   without branch lengths: hstrat ~0.6s vs treeswift ~1.0s (~0.7x)
def alifestd_from_newick(
    newick: str,
    *,
    branch_length_dtype: type = float,
    create_ancestor_list: bool = False,
) -> pd.DataFrame:
    """Convert a Newick format string to a phylogeny dataframe.

    Parses a Newick tree string and returns a pandas DataFrame in alife
    standard format with columns: id, ancestor_id, taxon_label,
    origin_time_delta, and branch_length. Optionally includes
    ancestor_list.

    Parameters
    ----------
    newick : str
        A phylogeny in Newick format.
    branch_length_dtype : type, default float
        Dtype for branch length values. Use ``int`` to get nullable integer
        columns (``pd.Int64Dtype``). Missing branch lengths will be ``pd.NA``
        for integer dtypes or ``NaN`` for float dtypes.
    create_ancestor_list : bool, default False
        If True, include an ``ancestor_list`` column in the result.

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
        columns = {
            "id": pd.Series(dtype=int),
            "ancestor_id": pd.Series(dtype=int),
            "taxon_label": pd.Series(dtype=str),
            "origin_time_delta": pd.Series(dtype=float),
            "branch_length": pd.Series(dtype=float),
        }
        if create_ancestor_list:
            columns["ancestor_list"] = pd.Series(dtype=str)
        return pd.DataFrame(columns)

    chars = np.frombuffer(newick.encode("ascii"), dtype=np.uint8)
    n = len(chars)

    (
        ids,
        ancestor_ids,
        branch_lengths,
        label_start_stops,
    ) = _parse_newick(newick, chars, n, branch_length_dtype)

    labels = _extract_labels(newick, chars, label_start_stops)

    # convert branch lengths to requested dtype with proper null handling
    np_dtype = np.dtype(branch_length_dtype)
    if np.issubdtype(np_dtype, np.integer):
        # use pandas nullable integer: NaN -> pd.NA
        bl_series = pd.array(
            np.where(np.isnan(branch_lengths), pd.NA, branch_lengths),
            dtype=pd.Int64Dtype(),
        )
        otd_series = bl_series.copy()
    else:
        bl_series = branch_lengths
        otd_series = branch_lengths.copy()

    phylogeny_df = pd.DataFrame(
        {
            "id": ids,
            "ancestor_id": ancestor_ids,
            "taxon_label": labels,
            "origin_time_delta": otd_series,
            "branch_length": bl_series,
        },
    )

    if create_ancestor_list:
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
        "--branch-length-dtype",
        type=str,
        choices=["float", "int"],
        default="float",
        help="Dtype for branch length values. Defaults to 'float'.",
    )
    parser.add_argument(
        "--create-ancestor-list",
        action="store_true",
        default=False,
        help="Include an ancestor_list column in the output.",
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


_dtype_lookup = {"float": float, "int": int}


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
        phylogeny_df = alifestd_from_newick(
            newick_str,
            branch_length_dtype=_dtype_lookup[args.branch_length_dtype],
            create_ancestor_list=args.create_ancestor_list,
        )

    output_ext = os.path.splitext(args.output_file)[1]
    output_kwargs = eval_kwargs(args.output_kwargs)

    logging.info(
        f"writing alife-standard {output_ext} phylogeny data to "
        f"{args.output_file}...",
    )
    if args.output_engine == "polars":
        phylogeny_df = pl.from_pandas(phylogeny_df)
        dispatch_writer = {
            ".csv": pl.DataFrame.write_csv,
            ".fea": pl.DataFrame.write_ipc,
            ".feather": pl.DataFrame.write_ipc,
            ".pqt": pl.DataFrame.write_parquet,
            ".parquet": pl.DataFrame.write_parquet,
        }
    elif args.output_engine == "pandas":
        if output_ext == ".csv":
            output_kwargs.setdefault("index", False)
        dispatch_writer = {
            ".csv": pd.DataFrame.to_csv,
            ".fea": pd.DataFrame.to_feather,
            ".feather": pd.DataFrame.to_feather,
            ".pqt": pd.DataFrame.to_parquet,
            ".parquet": pd.DataFrame.to_parquet,
        }
    else:
        raise ValueError(f"unsupported output engine: {args.output_engine!r}")

    dispatch_writer[output_ext](
        phylogeny_df,
        args.output_file,
        **output_kwargs,
    )

    logging.info("done!")
