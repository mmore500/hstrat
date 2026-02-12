import argparse
import logging
import os

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import numpy as np
import polars as pl

from ._alifestd_prune_extinct_lineages_asexual import (
    _create_has_extant_descendant_contiguous_sorted,
)
from ._configure_prod_logging import configure_prod_logging
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


def alifestd_prune_extinct_lineages_asexual_polars(
    phylogeny_df: pl.DataFrame,
) -> pl.DataFrame:
    """Drop taxa without extant descendants.

    An "extant" column, if provided, is used to determine extant taxa.
    Otherwise, taxa with inf or nan "destruction_time" are considered extant.

    Parameters
    ----------
    phylogeny_df : polars.DataFrame
        The phylogeny as a dataframe in alife standard format.

        Must represent an asexual phylogeny.

    Raises
    ------
    NotImplementedError
        If `phylogeny_df` has no "ancestor_id" column.
    NotImplementedError
        If `phylogeny_df` has non-contiguous ids.
    NotImplementedError
        If `phylogeny_df` is not topologically sorted.
    ValueError
        If `phylogeny_df` has neither "extant" or "destruction_time" columns.

    Returns
    -------
    polars.DataFrame
        The pruned phylogeny in alife standard format.
    """
    if isinstance(phylogeny_df, pl.LazyFrame):
        phylogeny_df = phylogeny_df.collect()

    if "ancestor_id" not in phylogeny_df.columns:
        raise NotImplementedError(
            "ancestor_id column required; ancestor_list not supported"
        )

    if phylogeny_df.is_empty():
        return phylogeny_df

    logging.info(
        "- alifestd_prune_extinct_lineages_asexual_polars: "
        "checking contiguous ids...",
    )
    has_contiguous_ids = phylogeny_df.select(
        pl.col("id").diff() == 1
    ).to_series().all() and (phylogeny_df["id"].first() == 0)
    if not has_contiguous_ids:
        raise NotImplementedError("non-contiguous ids not yet supported")

    logging.info(
        "- alifestd_prune_extinct_lineages_asexual_polars: "
        "checking topological sort...",
    )
    if (
        not phylogeny_df.select(pl.col("ancestor_id") <= pl.col("id"))
        .to_series()
        .all()
    ):
        raise NotImplementedError(
            "polars topological sort not yet implemented"
        )

    logging.info(
        "- alifestd_prune_extinct_lineages_asexual_polars: "
        "determining extant mask...",
    )
    if "extant" in phylogeny_df.columns:
        extant_mask = phylogeny_df["extant"].to_numpy().astype(bool)
    elif "destruction_time" in phylogeny_df.columns:
        destruction_time = phylogeny_df["destruction_time"]
        extant_mask = (
            destruction_time.is_nan() | destruction_time.is_infinite()
        ).to_numpy()
    else:
        raise ValueError('Need "extant" or "destruction_time" column.')

    logging.info(
        "- alifestd_prune_extinct_lineages_asexual_polars: "
        "calculating has_extant_descendant...",
    )
    # must copy to remove read-only flag for numba compatibility
    ancestor_ids = (
        phylogeny_df["ancestor_id"].to_numpy().astype(np.uint64).copy()
    )
    has_extant_descendant = _create_has_extant_descendant_contiguous_sorted(
        ancestor_ids,
        extant_mask.copy(),
    )

    logging.info(
        "- alifestd_prune_extinct_lineages_asexual_polars: filtering...",
    )
    return phylogeny_df.filter(pl.Series(has_extant_descendant))


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Drop taxa without extant descendants.

An "extant" column, if provided, is used to determine extant taxa.
Otherwise, taxa with inf or nan "destruction_time" are considered extant.

Data is assumed to be in alife standard format.
Only supports asexual phylogenies.

Additional Notes
================
- Requires 'ancestor_id' column to be present in input DataFrame.
Otherwise, no action is taken.

- Requires 'extant' or 'destruction_time' column.

- Use `--eager-read` if modifying data file inplace.

- This CLI entrypoint is experimental and may be subject to change.

See Also
========
hstrat._auxiliary_lib._alifestd_prune_extinct_lineages_asexual :
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
        dfcli_module="hstrat._auxiliary_lib._alifestd_prune_extinct_lineages_asexual_polars",
        dfcli_version=get_hstrat_version(),
    )
    return parser


if __name__ == "__main__":
    configure_prod_logging()

    parser = _create_parser()
    args, __ = parser.parse_known_args()

    try:
        with log_context_duration(
            "hstrat._auxiliary_lib._alifestd_prune_extinct_lineages_asexual_polars",
            logging.info,
        ):
            _run_dataframe_cli(
                base_parser=parser,
                output_dataframe_op=alifestd_prune_extinct_lineages_asexual_polars,
            )
    except NotImplementedError as e:
        logging.error(
            "- polars op not yet implemented, use pandas op CLI instead",
        )
        raise e
