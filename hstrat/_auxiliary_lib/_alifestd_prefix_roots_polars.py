import argparse
import logging
import numbers
import os
import typing
import warnings

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import numpy as np
import opytional as opyt
import polars as pl

from ._add_bool_arg import add_bool_arg
from ._alifestd_topological_sensitivity_warned_polars import (
    alifestd_topological_sensitivity_warned_polars,
)
from ._configure_prod_logging import configure_prod_logging
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


@alifestd_topological_sensitivity_warned_polars(
    insert=True,
    delete=False,
    update=True,
)
def alifestd_prefix_roots_polars(
    phylogeny_df: pl.DataFrame,
    *,
    allow_id_reassign: bool = False,
    origin_time: typing.Optional[numbers.Real] = None,
) -> pl.DataFrame:
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

    if "ancestor_list" in phylogeny_df:
        raise NotImplementedError
    if not allow_id_reassign:
        raise NotImplementedError
    if phylogeny_df.lazy().limit(1).collect().is_empty():
        raise NotImplementedError
    has_contiguous_ids = phylogeny_df.select(
        pl.col("id").diff() == 1
    ).to_series().all() and (phylogeny_df["id"].first() == 0)
    if not has_contiguous_ids:
        raise NotImplementedError

    phylogeny_df = phylogeny_df.drop("is_root", strict=False)

    logging.info("- alifestd_prefix_roots: marking eligible roots...")
    eligible_roots = (
        phylogeny_df.lazy()
        .with_columns(
            is_eligible=(
                pl.col("origin_time") > origin_time
                if origin_time is not None
                else True
            ),
            is_root=pl.col("id") == pl.col("ancestor_id"),
        )
        .select(
            pl.col("is_eligible") & pl.col("is_root"),
        )
        .collect()
        .to_series()
    )

    logging.info("- alifestd_prefix_roots: filtering prepended roots...")
    prepended_roots = (
        phylogeny_df.lazy()
        .filter(
            eligible_roots,
        )
        .select(
            "id",
            "origin_time",
            "ancestor_id",
        )
        .collect()
    )

    if "origin_time" in prepended_roots:
        logging.info("- alifestd_prefix_roots: setting origin time...")
        prepended_roots = prepended_roots.with_columns(
            origin_time=pl.lit(opyt.or_value(origin_time, 0))
        )

    logging.info("- alifestd_prefix_roots: updating phylogeny_df...")
    phylogeny_df = phylogeny_df.with_columns(
        id=pl.col("id") + pl.lit(len(prepended_roots)),
        ancestor_id=pl.col("ancestor_id") + pl.lit(len(prepended_roots)),
    )
    ancestor_ids = phylogeny_df["ancestor_id"].to_numpy().copy()
    ancestor_ids[prepended_roots["id"].to_numpy()] = np.arange(
        len(prepended_roots),
    )
    phylogeny_df = phylogeny_df.with_columns(
        ancestor_id=pl.Series(ancestor_ids),
    )

    logging.info("- alifestd_prefix_roots: updating prepended roots...")
    prepended_roots = prepended_roots.with_columns(
        id=pl.int_range(len(prepended_roots)),
        ancestor_id=pl.int_range(len(prepended_roots)),
    ).cast(
        {
            k: v
            for k, v in phylogeny_df.collect_schema().items()
            if k in prepended_roots.collect_schema()
        },
    )

    logging.info("- alifestd_prefix_roots: creating gather_indices...")
    gather_indices = np.empty(
        len(phylogeny_df) + len(prepended_roots), dtype=np.int64
    )
    gather_indices[: len(prepended_roots)] = np.arange(len(prepended_roots))
    gather_indices[len(prepended_roots) :] = np.arange(len(phylogeny_df))

    logging.info("- alifestd_prefix_roots: gathering and updating...")
    return (
        phylogeny_df.lazy()
        .select(pl.all().gather(gather_indices))
        .with_row_index()
        .with_columns(
            pl.when(pl.col("index") < len(prepended_roots))
            .then(None)
            .otherwise(pl.all())
            .name.keep()
        )
        .drop("index")
        .update(prepended_roots.lazy())
        .collect()
    )


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
        allow_abbrev=False,
        description=format_cli_description(_raw_description),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser = _add_parser_base(
        parser=parser,
        dfcli_module="hstrat._auxiliary_lib._alifestd_prefix_roots_polars",
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

    try:
        with log_context_duration(
            "hstrat._auxiliary_lib._alifestd_prefix_roots_polars",
            logging.info,
        ):
            _run_dataframe_cli(
                base_parser=parser,
                output_dataframe_op=lambda df: alifestd_prefix_roots_polars(
                    df,
                    allow_id_reassign=args.allow_id_reassign,
                    origin_time=args.origin_time,
                    ignore_topological_sensitivity=args.ignore_topological_sensitivity,
                    drop_topological_sensitivity=args.drop_topological_sensitivity,
                ),
            )
    except NotImplementedError as e:
        logging.error(
            "- polars op not yet implemented, use pandas op CLI instead",
        )
        raise e
