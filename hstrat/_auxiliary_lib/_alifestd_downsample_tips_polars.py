import argparse
import functools
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
from ._configure_prod_logging import configure_prod_logging
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


def _alifestd_downsample_tips_polars_impl(
    phylogeny_df: pl.DataFrame,
    n_downsample: int,
    seed: int,
) -> pl.DataFrame:
    """Implementation detail for alifestd_downsample_tips_polars."""

    logging.info(
        "- alifestd_downsample_tips_polars: finding leaf ids...",
    )
    marked_df = alifestd_mark_leaves_polars(phylogeny_df)

    logging.info(
        "- alifestd_downsample_tips_polars: collecting leaf ids...",
    )
    leaf_ids = (
        marked_df.lazy()
        .filter(pl.col("is_leaf"))
        .select(pl.col("id"))
        .collect()
        .to_series()
        .set_sorted()
    )

    logging.info(
        "- alifestd_downsample_tips_polars: sampling leaf_ids...",
    )
    leaf_ids = leaf_ids.sample(n=min(n_downsample, len(leaf_ids)), seed=seed)

    logging.info(
        "- alifestd_downsample_tips_polars: finding extant...",
    )
    phylogeny_df = phylogeny_df.with_columns(
        extant=pl.int_range(0, pl.len()).is_in(leaf_ids)  # contiguous ids
    )

    logging.info(
        "- alifestd_downsample_tips_polars: pruning...",
    )
    return alifestd_prune_extinct_lineages_polars(phylogeny_df).drop("extant")


@alifestd_topological_sensitivity_warned_polars(
    insert=False,
    delete=True,
    update=False,
)
def alifestd_downsample_tips_polars(
    phylogeny_df: pl.DataFrame,
    n_downsample: int,
    seed: typing.Optional[int] = None,
) -> pl.DataFrame:
    """Create a subsample phylogeny containing `n_downsample` tips.

    If `n_downsample` is greater than the number of tips in the phylogeny,
    the whole phylogeny is returned.

    Only supports asexual phylogenies.

    Parameters
    ----------
    phylogeny_df : polars.DataFrame
        The phylogeny as a dataframe in alife standard format.

        Must represent an asexual phylogeny.
    n_downsample : int
        Number of tips to retain.
    seed : int, optional
        Integer seed for deterministic behavior.

    Raises
    ------
    NotImplementedError
        If `phylogeny_df` has no "ancestor_id" column.

    Returns
    -------
    polars.DataFrame
        The downsampled phylogeny in alife standard format.

    See Also
    --------
    alifestd_downsample_tips_asexual :
        Pandas-based implementation.
    """
    if "ancestor_id" not in phylogeny_df.lazy().collect_schema().names():
        raise NotImplementedError("ancestor_id column required")

    if phylogeny_df.lazy().limit(1).collect().is_empty():
        return phylogeny_df

    return _alifestd_downsample_tips_polars_impl(
        phylogeny_df,
        n_downsample,
        seed=seed,
    )


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Create a subsample phylogeny containing `-n` tips.

If `-n` is greater than the number of tips in the phylogeny, the whole phylogeny is returned.

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
hstrat._auxiliary_lib._alifestd_downsample_tips_asexual :
    CLI entrypoint for Pandas-based implementation.
"""


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        add_help=False,
        description=format_cli_description(_raw_description),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser = _add_parser_base(
        parser=parser,
        dfcli_module="hstrat._auxiliary_lib._alifestd_downsample_tips_polars",
        dfcli_version=get_hstrat_version(),
    )
    parser.add_argument(
        "-n",
        default=sys.maxsize,
        type=int,
        help="Number of tips to subsample.",
    )
    parser.add_argument(
        "--seed",
        default=None,
        dest="seed",
        help="Integer seed for deterministic behavior.",
        type=int,
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
            "hstrat._auxiliary_lib._alifestd_downsample_tips_polars",
            logging.info,
        ):
            _run_dataframe_cli(
                base_parser=parser,
                output_dataframe_op=functools.partial(
                    alifestd_downsample_tips_polars,
                    n_downsample=args.n,
                    seed=args.seed,
                    ignore_topological_sensitivity=args.ignore_topological_sensitivity,
                    drop_topological_sensitivity=args.drop_topological_sensitivity,
                ),
                overridden_arguments="ignore",  # seed is overridden
            )
    except NotImplementedError as e:
        logging.error(
            "- polars op not yet implemented, use pandas op CLI instead",
        )
        raise e
