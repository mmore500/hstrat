import argparse
import functools
import logging
import numbers
import os
import typing
import warnings

from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import joinem
import numpy as np
import opytional as opyt
import pandas as pd

from ._add_bool_arg import add_bool_arg
from ._alifestd_has_contiguous_ids import alifestd_has_contiguous_ids
from ._alifestd_mark_roots import alifestd_mark_roots
from ._alifestd_topological_sensitivity_warned import (
    alifestd_topological_sensitivity_warned,
)
from ._configure_prod_logging import configure_prod_logging
from ._delegate_polars_implementation import delegate_polars_implementation
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


def _alifestd_prefix_roots_fast(
    phylogeny_df: pd.DataFrame,
    prepended_roots: pd.DataFrame,
) -> pd.DataFrame:
    """Fast path for cases with ancestor_id column present and id reassignemnt
    is allowed."""
    phylogeny_df.reset_index(drop=True, inplace=True)
    phylogeny_df["id"] += len(prepended_roots)
    phylogeny_df["ancestor_id"] += len(prepended_roots)
    phylogeny_df.loc[
        prepended_roots["id"],
        "ancestor_id",
    ] = np.arange(len(prepended_roots))

    prepended_roots["id"] = np.arange(len(prepended_roots))
    prepended_roots["ancestor_id"] = prepended_roots["id"]

    return pd.concat([prepended_roots, phylogeny_df], ignore_index=True)


@alifestd_topological_sensitivity_warned(
    insert=True,
    delete=False,
    update=True,
)
def alifestd_prefix_roots(
    phylogeny_df: pd.DataFrame,
    *,
    allow_id_reassign: bool = False,
    origin_time: typing.Optional[numbers.Real] = None,
    mutate: bool = False,
) -> pd.DataFrame:
    """Add new roots to the phylogeny, prefixing existing roots.

    An origin time may be specified, in which case only roots with origin times
    past the specified time will be prefixed. If no origin time is specified,
    all roots will be prefixed.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.
    """
    if "origin_time_delta" in phylogeny_df:
        warnings.warn("alifestd_prefix_roots ignores origin_time_delta values")
    if origin_time is not None and "origin_time" not in phylogeny_df:
        raise ValueError(
            "origin_time specified but not present in phylogeny dataframe",
        )

    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    phylogeny_df = alifestd_mark_roots(phylogeny_df, mutate=True)

    eligible_roots = (phylogeny_df["is_root"]) & (
        phylogeny_df["origin_time"] > origin_time
        if origin_time is not None
        else True
    )

    del phylogeny_df["is_root"]

    prepended_roots = phylogeny_df.loc[
        eligible_roots,
        [
            col
            for col in (
                "id",
                "origin_time",
                "ancestor_id",
                "ancestor_list",
            )
            if col in phylogeny_df
        ],
    ].copy()

    if "origin_time" in prepended_roots:
        prepended_roots["origin_time"] = opyt.or_value(origin_time, 0)

    if (
        "ancestor_id" in phylogeny_df
        and allow_id_reassign
        and "ancestor_list" not in phylogeny_df
        and alifestd_has_contiguous_ids(phylogeny_df)
    ):
        return _alifestd_prefix_roots_fast(
            phylogeny_df,
            prepended_roots,
        )

    prepended_roots["id"] = (
        phylogeny_df["id"].max() + 1 + np.arange(len(prepended_roots))
    )
    if "ancestor_id" in prepended_roots:
        prepended_roots["ancestor_id"] = prepended_roots["id"]
    if "ancestor_list" in prepended_roots:
        prepended_roots["ancestor_list"] = "[]"
    if phylogeny_df["id"].max() >= prepended_roots["id"].min():
        raise ValueError("overflow in new id assignment")

    if "ancestor_id" in phylogeny_df:
        phylogeny_df.loc[eligible_roots, "ancestor_id"] = prepended_roots[
            "id"
        ].values
    if "ancestor_list" in phylogeny_df:
        phylogeny_df.loc[eligible_roots, "ancestor_list"] = prepended_roots[
            "id"
        ].map("[{}]".format)

    return pd.concat([phylogeny_df, prepended_roots], ignore_index=True)


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Add new roots to the phylogeny, prefixing existing roots.

Data is assumed to be in alife standard format.

Additional Notes
================
- Use `--eager-read` if modifying data file inplace.

- This CLI entrypoint is experimental and may be subject to change.
"""

def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        add_help=False,
        description=format_cli_description(_raw_description),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser = _add_parser_base(
        parser=parser,
        dfcli_module="hstrat._auxiliary_lib._alifestd_prefix_roots",
        dfcli_version=get_hstrat_version(),
    )
    add_bool_arg(
        parser,
        "allow-id-reassign",
        default=False,
        help="allow reassignment of ids (default: False)",
    )
    parser.add_argument(
        "--origin-time",
        type=float,
        default=None,
        help="origin time for new root nodes (default: None)",
    )
    add_bool_arg(
        parser,
        "ignore-topological-sensitivity",
        default=False,
        help="suppress topological sensitivity warning (default: False)",
    )
    add_bool_arg(
        parser,
        "drop-topological-sensitivity",
        default=False,
        help="drop topology-sensitive columns from output (default: False)",
    )
    return parser


if __name__ == "__main__":
    configure_prod_logging()

    parser = _create_parser()
    args, __ = parser.parse_known_args()
    with log_context_duration(
        "hstrat._auxiliary_lib._alifestd_prefix_roots", logging.info
    ):
        _run_dataframe_cli(
            base_parser=parser,
            output_dataframe_op=delegate_polars_implementation()(
                functools.partial(
                    alifestd_prefix_roots,
                    allow_id_reassign=args.allow_id_reassign,
                    origin_time=args.origin_time,
                    ignore_topological_sensitivity=args.ignore_topological_sensitivity,
                    drop_topological_sensitivity=args.drop_topological_sensitivity,
                ),
            ),
        )
