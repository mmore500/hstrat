import argparse
import functools
import gc
import logging
import os
import sys
import typing

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import polars as pl

from ._add_bool_arg import add_bool_arg
from ._alifestd_mark_leaves_polars import alifestd_mark_leaves_polars
from ._alifestd_prune_extinct_lineages_polars import (
    alifestd_prune_extinct_lineages_polars,
)
from ._alifestd_topological_sensitivity_warned_polars import (
    alifestd_topological_sensitivity_warned_polars,
)
from ._begin_prod_logging import begin_prod_logging
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration
from ._log_memory_usage import log_memory_usage


@alifestd_topological_sensitivity_warned_polars(
    insert=False,
    delete=True,
    update=False,
)
def alifestd_downsample_tips_canopy_polars(
    phylogeny_df: pl.DataFrame,
    num_tips: typing.Optional[int] = None,
    criterion: str = "origin_time",
) -> pl.DataFrame:
    """Retain the `num_tips` leaves with the largest `criterion` values and
    prune extinct lineages.

    If `num_tips` is ``None``, it defaults to the number of leaves that
    share the maximum value of the `criterion` column. If `num_tips` is
    greater than or equal to the number of leaves in the phylogeny, the
    whole phylogeny is returned. Ties are broken arbitrarily.

    Only supports asexual phylogenies.

    Parameters
    ----------
    phylogeny_df : polars.DataFrame
        The phylogeny as a dataframe in alife standard format.

        Must represent an asexual phylogeny.
    num_tips : int, optional
        Number of tips to retain. If ``None``, defaults to the count of
        leaves with the maximum `criterion` value.
    criterion : str, default "origin_time"
        Column name used to rank leaves. The `num_tips` leaves with the
        largest values in this column are retained. Ties are broken
        arbitrarily.

    Raises
    ------
    NotImplementedError
        If `phylogeny_df` has no "ancestor_id" column.
    ValueError
        If `criterion` is not a column in `phylogeny_df`.

    Returns
    -------
    polars.DataFrame
        The pruned phylogeny in alife standard format.

    See Also
    --------
    alifestd_downsample_tips_canopy_asexual :
        Pandas-based implementation.
    """
    logging.info(
        "- alifestd_downsample_tips_canopy_polars: collecting schema...",
    )
    schema_names = phylogeny_df.lazy().collect_schema().names()
    gc.collect()
    log_memory_usage(logging.info)
    if criterion not in schema_names:
        raise ValueError(
            f"criterion column {criterion!r} not found in phylogeny_df",
        )

    if "ancestor_id" not in schema_names:
        raise NotImplementedError("ancestor_id column required")

    logging.info(
        "- alifestd_downsample_tips_canopy_polars: checking empty...",
    )
    if phylogeny_df.lazy().limit(1).collect().is_empty():
        return phylogeny_df

    logging.info(
        "- alifestd_downsample_tips_canopy_polars: finding leaf ids...",
    )
    phylogeny_df = alifestd_mark_leaves_polars(phylogeny_df)
    gc.collect()
    log_memory_usage(logging.info)

    logging.info(
        "- alifestd_downsample_tips_canopy_polars: selecting top leaf_ids...",
    )
    leaves_lazy = phylogeny_df.lazy().filter(pl.col("is_leaf"))
    if num_tips is None:
        max_val = leaves_lazy.select(pl.col(criterion).max()).collect().item()
        num_tips = (
            leaves_lazy.filter(pl.col(criterion) == max_val)
            .select(pl.len())
            .collect()
            .item()
        )
        gc.collect()
        log_memory_usage(logging.info)

    logging.info(
        "- alifestd_downsample_tips_canopy_polars: counting leaves...",
    )
    total_leaves = leaves_lazy.select(pl.len()).collect().item()
    logging.info(
        f"- alifestd_downsample_tips_canopy_polars: {total_leaves=}...",
    )

    if num_tips >= total_leaves:
        logging.info(
            "- alifestd_downsample_tips_canopy_polars: taking all...",
        )
        leaf_ids = leaves_lazy.select(pl.col("id")).collect().to_series()
    else:  # split case to prevent extreme top_k crash where num_tips is high
        logging.info(
            "- alifestd_downsample_tips_canopy_polars: taking top k...",
        )
        leaf_ids = (
            leaves_lazy.top_k(num_tips, by=pl.col(criterion))
            .select(pl.col("id"))
            .collect()
            .to_series()
        )
    gc.collect()
    log_memory_usage(logging.info)

    logging.info(
        "- alifestd_downsample_tips_canopy_polars: marking extant...",
    )
    phylogeny_df = phylogeny_df.with_columns(
        extant=pl.col("id").is_in(leaf_ids),
    )
    del leaf_ids
    gc.collect()
    log_memory_usage(logging.info)

    logging.info(
        "- alifestd_downsample_tips_canopy_polars: pruning...",
    )
    return alifestd_prune_extinct_lineages_polars(phylogeny_df).drop("extant")


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Retain the `-n` leaves with the largest `--criterion` values and prune extinct lineages.

If `-n` is greater than or equal to the number of leaves in the phylogeny, the whole phylogeny is returned. Ties are broken arbitrarily.

Data is assumed to be in alife standard format.
Only supports asexual phylogenies.

Additional Notes
================
- Requires 'ancestor_id' column to be present in input DataFrame.
Otherwise, no action is taken.

- Use `--eager-read` if modifying data file inplace.

- This CLI entrypoint is experimental and may be subject to change.

See Also
========
hstrat._auxiliary_lib._alifestd_downsample_tips_canopy_asexual :
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
        dfcli_module="hstrat._auxiliary_lib._alifestd_downsample_tips_canopy_polars",
        dfcli_version=get_hstrat_version(),
    )
    parser.add_argument(
        "-n",
        default=sys.maxsize,
        type=int,
        help="Number of tips to retain.",
    )
    parser.add_argument(
        "--criterion",
        default="origin_time",
        type=str,
        help="Column name used to rank leaves; ties broken arbitrarily (default: origin_time).",
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
    begin_prod_logging()

    parser = _create_parser()
    args, __ = parser.parse_known_args()

    try:
        with log_context_duration(
            "hstrat._auxiliary_lib._alifestd_downsample_tips_canopy_polars",
            logging.info,
        ):
            _run_dataframe_cli(
                base_parser=parser,
                output_dataframe_op=functools.partial(
                    alifestd_downsample_tips_canopy_polars,
                    num_tips=args.n,
                    criterion=args.criterion,
                    ignore_topological_sensitivity=args.ignore_topological_sensitivity,
                    drop_topological_sensitivity=args.drop_topological_sensitivity,
                ),
            )
    except NotImplementedError as e:
        logging.error(
            "- polars op not yet implemented, use pandas op CLI instead",
        )
        raise e
