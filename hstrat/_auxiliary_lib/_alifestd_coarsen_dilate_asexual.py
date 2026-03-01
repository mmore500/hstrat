import argparse
import functools
import logging
import os
import typing

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import numpy as np
import pandas as pd

from ._add_bool_arg import add_bool_arg
from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_is_topologically_sorted import alifestd_is_topologically_sorted
from ._alifestd_make_ancestor_list_col import alifestd_make_ancestor_list_col
from ._alifestd_mark_leaves import alifestd_mark_leaves
from ._alifestd_topological_sensitivity_warned import (
    alifestd_topological_sensitivity_warned,
)
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._begin_prod_logging import begin_prod_logging
from ._delegate_polars_implementation import delegate_polars_implementation
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._jit import jit
from ._log_context_duration import log_context_duration


@jit(nopython=True)
def _alifestd_coarsen_dilate_impl(
    ancestor_ids: np.ndarray,
    criterion_values: np.ndarray,
    is_leaf: np.ndarray,
    dilation: int,
) -> typing.Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Single-pass coarsen-dilate implementation.

    For each inner node, shift its criterion value to the nearest
    ``n % dilation == 0`` boundary at or below its current value.  Then
    merge consecutive inner nodes that land on the same boundary, by
    re-pointing children to the earliest (topologically first) node at
    that boundary along each lineage.

    Returns
    -------
    ancestor_ids : np.ndarray
        Updated ancestor ids.
    criterion_values : np.ndarray
        Updated criterion values.
    keep_mask : np.ndarray
        Boolean mask of rows to keep.
    """
    n = len(ancestor_ids)
    # For each node, which representative node it maps to after merging.
    representative = np.arange(n)
    keep_mask = np.ones(n, dtype=np.bool_)
    new_criterion = criterion_values.copy()

    for idx, anc in enumerate(ancestor_ids):
        if is_leaf[idx]:
            # Tips never move; just update ancestor to representative.
            ancestor_ids[idx] = representative[anc]
            continue

        anc_rep = representative[anc]
        if anc_rep == idx:
            # Root node (self-referencing) — always keep, snap in place
            new_criterion[idx] = (criterion_values[idx] // dilation) * dilation
            ancestor_ids[idx] = idx
            continue

        # Snap inner node criterion to floor boundary
        val = criterion_values[idx]
        # Use floor division for both int and float
        snapped = (val // dilation) * dilation
        new_criterion[idx] = snapped

        # Check if this inner node should merge with its ancestor's
        # representative: they merge when both are inner nodes that
        # snapped to the same boundary value.
        anc_rep_snapped = new_criterion[anc_rep]
        if not is_leaf[anc_rep] and snapped == anc_rep_snapped:
            # Merge: this node collapses into anc_rep
            representative[idx] = anc_rep
            keep_mask[idx] = False
            ancestor_ids[idx] = ancestor_ids[anc_rep]
        else:
            # Keep this node, but re-point ancestor
            ancestor_ids[idx] = anc_rep

    # Final pass: update all ancestor_ids to point to representatives
    for idx, _anc in enumerate(ancestor_ids):
        ancestor_ids[idx] = representative[ancestor_ids[idx]]

    return ancestor_ids, new_criterion, keep_mask


@alifestd_topological_sensitivity_warned(
    insert=False,
    delete=True,
    update=True,
)
def alifestd_coarsen_dilate_asexual(
    phylogeny_df: pd.DataFrame,
    *,
    criterion: str = "origin_time",
    dilation: int = 1,
    mutate: bool = False,
) -> pd.DataFrame:
    """Coarsen a phylogeny by collapsing inner nodes within dilation windows.

    All inner (non-leaf) nodes with criterion values in the half-open
    interval ``[n, n + dilation)``, where ``n % dilation == 0``, are
    collapsed to a single inner node at ``n``.

    Tip nodes are never moved. The MRCA of two tips may only shift
    backward (never forward), by at most ``dilation`` units, and never
    across a ``n % dilation == 0`` boundary.

    Parameters
    ----------
    phylogeny_df : pd.DataFrame
        Input phylogeny in alife standard format.
    criterion : str, default "origin_time"
        Column whose values define the time axis for dilation.
    dilation : int
        Width of the dilation window.  Must be a positive integer.
    mutate : bool, default False
        If True, allow in-place mutation of the input dataframe.

    Returns
    -------
    pd.DataFrame
        Coarsened phylogeny in alife standard format.

    Raises
    ------
    NotImplementedError
        If input is not topologically sorted with contiguous ids.
    ValueError
        If *dilation* is not a positive integer, if *criterion* is not
        present in *phylogeny_df*, or if *criterion* is ``"id"`` or
        ``"ancestor_id"``.
    """
    if dilation <= 0:
        raise ValueError(f"dilation must be positive, got {dilation}")

    if criterion in ("id", "ancestor_id"):
        raise ValueError(
            f"criterion must not be 'id' or 'ancestor_id', got {criterion!r}",
        )

    if criterion not in phylogeny_df.columns:
        raise ValueError(
            f"criterion column {criterion!r} not found in phylogeny_df",
        )

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)
    if "ancestor_id" not in phylogeny_df.columns:
        raise ValueError("asexual phylogeny required")

    if not alifestd_is_topologically_sorted(phylogeny_df):
        raise NotImplementedError(
            "alifestd_coarsen_dilate_asexual requires topologically "
            "sorted input",
        )
    if not alifestd_has_contiguous_ids(phylogeny_df):
        raise NotImplementedError(
            "alifestd_coarsen_dilate_asexual requires contiguous ids",
        )

    phylogeny_df.reset_index(drop=True, inplace=True)

    had_is_leaf = "is_leaf" in phylogeny_df.columns
    phylogeny_df = alifestd_mark_leaves(phylogeny_df, mutate=True)

    ancestor_ids = phylogeny_df["ancestor_id"].values.copy()
    criterion_values = phylogeny_df[criterion].values.copy()
    is_leaf = phylogeny_df["is_leaf"].values

    (
        new_ancestor_ids,
        new_criterion_values,
        keep_mask,
    ) = _alifestd_coarsen_dilate_impl(
        ancestor_ids,
        criterion_values,
        is_leaf,
        dilation,
    )

    phylogeny_df["ancestor_id"] = new_ancestor_ids
    phylogeny_df[criterion] = new_criterion_values

    # Filter to kept rows
    phylogeny_df = phylogeny_df.loc[keep_mask].reset_index(drop=True)

    if not had_is_leaf:
        phylogeny_df.drop(columns=["is_leaf"], inplace=True)

    if "ancestor_list" in phylogeny_df.columns:
        phylogeny_df["ancestor_list"] = alifestd_make_ancestor_list_col(
            phylogeny_df["id"],
            phylogeny_df["ancestor_id"],
        )

    return phylogeny_df


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Coarsen a phylogeny by collapsing inner nodes within dilation windows.

All inner (non-leaf) nodes with criterion values in [n, n + dilation),
where n mod dilation == 0, are collapsed to a single inner node at n.

Tip nodes are never moved.

Data is assumed to be in alife standard format.
Only supports asexual phylogenies.

Additional Notes
================
- Requires topologically sorted input with contiguous ids.

- Requires 'ancestor_id' column to be present in input DataFrame.

- Use `--eager-read` if modifying data file inplace.

- This CLI entrypoint is experimental and may be subject to change.
"""


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        add_help=False,
        allow_abbrev=False,
        description=format_cli_description(_raw_description),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser = _add_parser_base(
        parser=parser,
        dfcli_module="hstrat._auxiliary_lib._alifestd_coarsen_dilate_asexual",
        dfcli_version=get_hstrat_version(),
    )
    parser.add_argument(
        "--criterion",
        default="origin_time",
        type=str,
        help="Column whose values define the time axis (default: origin_time).",
    )
    parser.add_argument(
        "--dilation",
        default=1,
        type=int,
        help="Width of the dilation window (default: 1).",
    )
    add_bool_arg(
        parser,
        "drop-topological-sensitivity",
        default=False,
        help="drop topology-sensitive columns from output (default: False)",
    )
    add_bool_arg(
        parser,
        "ignore-topological-sensitivity",
        default=False,
        help="suppress topological sensitivity warning (default: False)",
    )
    return parser


if __name__ == "__main__":
    begin_prod_logging()

    parser = _create_parser()
    args, __ = parser.parse_known_args()
    with log_context_duration(
        "hstrat._auxiliary_lib._alifestd_coarsen_dilate_asexual",
        logging.info,
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=delegate_polars_implementation()(
                functools.partial(
                    alifestd_coarsen_dilate_asexual,
                    criterion=args.criterion,
                    dilation=args.dilation,
                    drop_topological_sensitivity=args.drop_topological_sensitivity,
                    ignore_topological_sensitivity=args.ignore_topological_sensitivity,
                ),
            ),
        )
