import argparse
import functools
import logging
import os
import sys

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import polars as pl

from ._alifestd_mark_leaves_polars import alifestd_mark_leaves_polars
from ._alifestd_prune_extinct_lineages_polars import (
    alifestd_prune_extinct_lineages_polars,
)
from ._configure_prod_logging import configure_prod_logging
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


def alifestd_prune_canopy_polars(
    phylogeny_df: pl.DataFrame,
    num_tips: int,
) -> pl.DataFrame:
    """Retain the `num_tips` leaves with the highest ids and prune extinct
    lineages.

    If `num_tips` is greater than or equal to the number of leaves in the
    phylogeny, the whole phylogeny is returned.

    Only supports asexual phylogenies.

    Parameters
    ----------
    phylogeny_df : polars.DataFrame
        The phylogeny as a dataframe in alife standard format.

        Must represent an asexual phylogeny.
    num_tips : int
        Number of tips to retain.

    Raises
    ------
    NotImplementedError
        If `phylogeny_df` has no "ancestor_id" column.

    Returns
    -------
    polars.DataFrame
        The pruned phylogeny in alife standard format.

    See Also
    --------
    alifestd_prune_canopy_asexual :
        Pandas-based implementation.
    """
    if "ancestor_id" not in phylogeny_df.lazy().collect_schema().names():
        raise NotImplementedError("ancestor_id column required")

    if phylogeny_df.lazy().limit(1).collect().is_empty():
        return phylogeny_df

    logging.info(
        "- alifestd_prune_canopy_polars: finding leaf ids...",
    )
    marked_df = alifestd_mark_leaves_polars(phylogeny_df)

    logging.info(
        "- alifestd_prune_canopy_polars: collecting leaf ids...",
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
        "- alifestd_prune_canopy_polars: selecting top leaf_ids...",
    )
    leaf_ids = leaf_ids.sort(descending=True).head(num_tips)

    logging.info(
        "- alifestd_prune_canopy_polars: marking extant...",
    )
    phylogeny_df = phylogeny_df.with_columns(
        extant=pl.int_range(0, pl.len()).is_in(leaf_ids)  # contiguous ids
    )

    logging.info(
        "- alifestd_prune_canopy_polars: pruning...",
    )
    return alifestd_prune_extinct_lineages_polars(phylogeny_df).drop("extant")


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Retain the `-n` leaves with the highest ids and prune extinct lineages.

If `-n` is greater than or equal to the number of leaves in the phylogeny, the whole phylogeny is returned.

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
hstrat._auxiliary_lib._alifestd_prune_canopy_asexual :
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
        dfcli_module="hstrat._auxiliary_lib._alifestd_prune_canopy_polars",
        dfcli_version=get_hstrat_version(),
    )
    parser.add_argument(
        "-n",
        default=sys.maxsize,
        type=int,
        help="Number of tips to retain.",
    )
    return parser


if __name__ == "__main__":
    configure_prod_logging()

    parser = _create_parser()
    args, __ = parser.parse_known_args()

    try:
        with log_context_duration(
            "hstrat._auxiliary_lib._alifestd_prune_canopy_polars",
            logging.info,
        ):
            _run_dataframe_cli(
                base_parser=parser,
                output_dataframe_op=functools.partial(
                    alifestd_prune_canopy_polars,
                    num_tips=args.n,
                ),
            )
    except NotImplementedError as e:
        logging.error(
            "- polars op not yet implemented, use pandas op CLI instead",
        )
        raise e
