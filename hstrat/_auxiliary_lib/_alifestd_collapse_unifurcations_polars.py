import argparse
import logging
import os
import warnings

import joinem
from joinem._dataframe_cli import _add_parser_base, _run_dataframe_cli
import polars as pl

from ._alifestd_assign_contiguous_ids_polars import (
    alifestd_assign_contiguous_ids_polars,
)
from ._alifestd_collapse_unifurcations import _collapse_unifurcations
from ._configure_prod_logging import configure_prod_logging
from ._format_cli_description import format_cli_description
from ._get_hstrat_version import get_hstrat_version
from ._log_context_duration import log_context_duration


def alifestd_collapse_unifurcations_polars(
    phylogeny_df: pl.DataFrame,
) -> pl.DataFrame:
    """Pare record to bypass organisms with one ancestor and one descendant.

    Input dataframe is not mutated by this operation unless `mutate` set True.
    If mutate set True, operation does not occur in place; still use return
    value to get transformed phylogeny dataframe.

    See Also
    --------
    alifestd_collapse_unifurcations :
        Pandas-based implementation.
    """
    phylogeny_df = phylogeny_df.lazy().collect()  # lazy not yet implemented

    if any(
        col in phylogeny_df
        for col in ["branch_length", "edge_length", "origin_time_delta"]
    ):
        warnings.warn(
            "alifestd_collapse_unifurcations does not update branch length "
            "columns. Use `origin_time` to recalculate branch lengths for "
            "collapsed phylogeny."
        )

    if "ancestor_list" in phylogeny_df:
        raise NotImplementedError

    original_ids = phylogeny_df["id"]
    has_contiguous_ids = phylogeny_df.select(
        pl.col("id").diff() == 1
    ).to_series().all() and (phylogeny_df["id"].first() == 0)
    if not has_contiguous_ids:
        logging.info(
            "- alifestd_collapse_unifurcations_polars: assigning ids...",
        )
        phylogeny_df = alifestd_assign_contiguous_ids_polars(phylogeny_df)

    if (
        not phylogeny_df.select(pl.col("ancestor_id") <= pl.col("id"))
        .to_series()
        .all()
    ):
        raise NotImplementedError(
            "polars topological sort not yet implemented",
        )

    logging.info(
        "- alifestd_collapse_unifurcations_polars: calculating reindex...",
    )
    keep_filter, ancestor_ids = _collapse_unifurcations(
        # must copy to remove read-only flag for numba compatibility
        phylogeny_df["ancestor_id"]
        .to_numpy()
        .copy(),
    )

    logging.info(
        "- alifestd_collapse_unifurcations_polars: applying reindex...",
    )
    return phylogeny_df.filter(keep_filter).with_columns(
        id=original_ids.to_numpy()[keep_filter],
        ancestor_id=original_ids.gather(ancestor_ids[keep_filter]),
    )


_raw_description = f"""{os.path.basename(__file__)} | (hstrat v{get_hstrat_version()}/joinem v{joinem.__version__})

Pare record to bypass organisms with one ancestor and one descendant.

Data is assumed to be in alife standard format.
Only supports asexual phylogenies.

Additional Notes
================
- Requires 'ancestor_id' column to be present in input DataFrame.

- Use `--eager-read` if modifying data file inplace.

- This CLI entrypoint is experimental and may be subject to change.

See Also
========
hstrat._auxiliary_lib._alifestd_collapse_unifurcations :
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
        dfcli_module="hstrat._auxiliary_lib._alifestd_collapse_unifurcations_polars",
        dfcli_version=get_hstrat_version(),
    )
    return parser


if __name__ == "__main__":
    configure_prod_logging()

    parser = _create_parser()
    args, __ = parser.parse_known_args()

    try:
        with log_context_duration(
            "hstrat._auxiliary_lib._alifestd_collapse_unifurcations_polars",
            logging.info,
        ):
            _run_dataframe_cli(
                base_parser=parser,
                output_dataframe_op=alifestd_collapse_unifurcations_polars,
            )
    except NotImplementedError as e:
        logging.error(
            "- polars op not yet implemented, use pandas op CLI instead",
        )
        raise e
