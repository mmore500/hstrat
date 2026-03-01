import argparse
import functools
import logging
import os
import typing

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import numpy as np
import polars as pl

from ._add_bool_arg import add_bool_arg
from ._alifestd_coarsen_dilate_asexual import _alifestd_coarsen_dilate_impl
from ._alifestd_has_contiguous_ids_polars import (
    alifestd_has_contiguous_ids_polars,
)
from ._alifestd_is_topologically_sorted_polars import (
    alifestd_is_topologically_sorted_polars,
)
from ._alifestd_mark_leaves_polars import alifestd_mark_leaves_polars
from ._alifestd_topological_sensitivity_warned_polars import (
    alifestd_topological_sensitivity_warned_polars,
)
from ._begin_prod_logging import begin_prod_logging
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


@alifestd_topological_sensitivity_warned_polars(
    insert=False,
    delete=True,
    update=True,
)
def alifestd_coarsen_dilate_polars(
    phylogeny_df: typing.Union[pl.DataFrame, pl.LazyFrame],
    *,
    criterion: str = "origin_time",
    dilation: int,
) -> pl.DataFrame:
    """Coarsen a phylogeny by collapsing inner nodes within dilation windows.

    All inner (non-leaf) nodes with criterion values in the half-open
    interval ``[n, n + dilation)``, where ``n % dilation == 0``, are
    collapsed to a single inner node at ``n``.

    Tip nodes are never moved. The MRCA of two tips may only shift
    backward (never forward), by at most ``dilation`` units, and never
    across a ``n % dilation == 0`` boundary.

    Parameters
    ----------
    phylogeny_df : polars.DataFrame or polars.LazyFrame
        Input phylogeny in alife standard format.
    criterion : str, default "origin_time"
        Column whose values define the time axis for dilation.
    dilation : int
        Width of the dilation window.  Must be a positive integer.

    Returns
    -------
    polars.DataFrame
        Coarsened phylogeny in alife standard format.

    Raises
    ------
    NotImplementedError
        If input is not topologically sorted with contiguous ids.
    ValueError
        If *dilation* is not a positive integer, if *criterion* is not
        present in *phylogeny_df*, or if *criterion* is ``"id"`` or
        ``"ancestor_id"``.

    See Also
    --------
    alifestd_coarsen_dilate_asexual :
        Pandas-based implementation.
    """
    if dilation <= 0:
        raise ValueError(f"dilation must be positive, got {dilation}")

    if criterion in ("id", "ancestor_id"):
        raise ValueError(
            f"criterion must not be 'id' or 'ancestor_id', got {criterion!r}",
        )

    logging.info(
        "- alifestd_coarsen_dilate_polars: collecting schema...",
    )
    schema_names = phylogeny_df.lazy().collect_schema().names()

    if criterion not in schema_names:
        raise ValueError(
            f"criterion column {criterion!r} not found in phylogeny_df",
        )

    if "ancestor_list" in schema_names:
        raise NotImplementedError(
            "ancestor_list column not supported in polars implementation",
        )

    if "ancestor_id" not in schema_names:
        raise ValueError("asexual phylogeny required")

    logging.info(
        "- alifestd_coarsen_dilate_polars: checking empty...",
    )
    if phylogeny_df.lazy().limit(1).collect().is_empty():
        return phylogeny_df.lazy().collect()

    logging.info(
        "- alifestd_coarsen_dilate_polars: collecting original ids...",
    )
    original_ids = (
        phylogeny_df.lazy().select("id").collect().to_series().to_numpy()
    )

    logging.info(
        "- alifestd_coarsen_dilate_polars: checking contiguous ids...",
    )
    if not alifestd_has_contiguous_ids_polars(phylogeny_df):
        raise NotImplementedError(
            "alifestd_coarsen_dilate_polars requires contiguous ids",
        )

    logging.info(
        "- alifestd_coarsen_dilate_polars: checking topological sort...",
    )
    if not alifestd_is_topologically_sorted_polars(phylogeny_df):
        raise NotImplementedError(
            "alifestd_coarsen_dilate_polars requires topologically "
            "sorted input",
        )

    logging.info(
        "- alifestd_coarsen_dilate_polars: collecting ancestor_ids...",
    )
    ancestor_ids = (
        phylogeny_df.lazy()
        .select("ancestor_id")
        .collect()
        .to_series()
        .to_numpy()
        .copy()
    )

    logging.info(
        "- alifestd_coarsen_dilate_polars: collecting criterion values...",
    )
    criterion_values = (
        phylogeny_df.lazy()
        .select(criterion)
        .collect()
        .to_series()
        .to_numpy()
        .copy()
    )

    logging.info(
        "- alifestd_coarsen_dilate_polars: marking leaves...",
    )
    phylogeny_df_with_leaves = alifestd_mark_leaves_polars(phylogeny_df)
    is_leaf = (
        phylogeny_df_with_leaves.lazy()
        .select("is_leaf")
        .collect()
        .to_series()
        .to_numpy()
    )

    logging.info(
        "- alifestd_coarsen_dilate_polars: running coarsen dilate...",
    )
    new_ancestor_ids, new_criterion_values, keep_mask = (
        _alifestd_coarsen_dilate_impl(
            ancestor_ids,
            criterion_values,
            is_leaf,
            dilation,
        )
    )

    logging.info(
        "- alifestd_coarsen_dilate_polars: applying results...",
    )
    return (
        phylogeny_df.lazy()
        .collect()
        .filter(keep_mask)
        .with_columns(
            id=original_ids[keep_mask],
            ancestor_id=original_ids[new_ancestor_ids[keep_mask]],
            **{criterion: new_criterion_values[keep_mask]},
        )
    )


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

See Also
========
hstrat._auxiliary_lib._alifestd_coarsen_dilate_asexual :
    CLI entrypoint for Pandas-based implementation.
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
        dfcli_module="hstrat._auxiliary_lib._alifestd_coarsen_dilate_polars",
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
        required=True,
        type=int,
        help="Width of the dilation window.",
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

    try:
        with log_context_duration(
            "hstrat._auxiliary_lib._alifestd_coarsen_dilate_polars",
            logging.info,
        ):
            _run_dataframe_cli(
                base_parser=parser,
                output_dataframe_op=functools.partial(
                    alifestd_coarsen_dilate_polars,
                    criterion=args.criterion,
                    dilation=args.dilation,
                    drop_topological_sensitivity=args.drop_topological_sensitivity,
                    ignore_topological_sensitivity=args.ignore_topological_sensitivity,
                ),
            )
    except NotImplementedError as e:
        logging.error(
            "- polars op not yet implemented, use pandas op CLI instead",
        )
        raise e
